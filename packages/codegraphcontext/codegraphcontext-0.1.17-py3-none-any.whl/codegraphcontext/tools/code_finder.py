# src/codegraphcontext/tools/code_finder.py
import logging
import re
from typing import Any, Dict, List
from pathlib import Path

from ..core.database import DatabaseManager

logger = logging.getLogger(__name__)

class CodeFinder:
    """Module for finding relevant code snippets and analyzing relationships."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.driver = self.db_manager.get_driver()

    def find_by_function_name(self, search_term: str) -> List[Dict]:
        """Find functions by name matching using the full-text index."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes("code_search_index", $search_term) YIELD node, score
                WITH node, score
                WHERE node:Function AND node.name CONTAINS $search_term
                RETURN node.name as name, node.file_path as file_path, node.line_number as line_number,
                       node.source as source, node.docstring as docstring, node.is_dependency as is_dependency
                ORDER BY score DESC
                LIMIT 20
            """, search_term=search_term)
            return [dict(record) for record in result]
    
    def find_by_class_name(self, search_term: str) -> List[Dict]:
        """Find classes by name matching using the full-text index."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes("code_search_index", $search_term) YIELD node, score
                WITH node, score
                WHERE node:Class AND node.name CONTAINS $search_term
                RETURN node.name as name, node.file_path as file_path, node.line_number as line_number,
                       node.source as source, node.docstring as docstring, node.is_dependency as is_dependency
                ORDER BY score DESC
                LIMIT 20
            """, search_term=search_term)
            return [dict(record) for record in result]

    def find_by_variable_name(self, search_term: str) -> List[Dict]:
        """Find variables by name matching"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Variable)
                WHERE v.name CONTAINS $search_term OR v.name =~ $regex_pattern
                RETURN v.name as name, v.file_path as file_path, v.line_number as line_number,
                       v.value as value, v.context as context, v.is_dependency as is_dependency
                ORDER BY v.is_dependency ASC, v.name
                LIMIT 20
            """, search_term=search_term, regex_pattern=f"(?i).*{re.escape(search_term)}.*")
            
            return [dict(record) for record in result]
    
    def find_by_content(self, search_term: str) -> List[Dict]:
        """Find code by content matching in source or docstrings using the full-text index."""
        with self.driver.session() as session:
            result = session.run("""
                CALL db.index.fulltext.queryNodes("code_search_index", $search_term) YIELD node, score
                WITH node, score
                WHERE node:Function OR node:Class OR node:Variable
                RETURN
                    CASE 
                        WHEN node:Function THEN 'function'
                        WHEN node:Class THEN 'class'
                        ELSE 'variable' 
                    END as type,
                    node.name as name, node.file_path as file_path,
                    node.line_number as line_number, node.source as source,
                    node.docstring as docstring, node.is_dependency as is_dependency
                ORDER BY score DESC
                LIMIT 20
            """, search_term=search_term)
            return [dict(record) for record in result]
    
    def find_related_code(self, user_query: str) -> Dict[str, Any]:
        """Find code related to a query using multiple search strategies"""
        results = {
            "query": user_query,
            "functions_by_name": self.find_by_function_name(user_query),
            "classes_by_name": self.find_by_class_name(user_query),
            "variables_by_name": self.find_by_variable_name(user_query),
            "content_matches": self.find_by_content(user_query)
        }
        
        all_results = []
        
        for func in results["functions_by_name"]:
            func["search_type"] = "function_name"
            func["relevance_score"] = 0.9 if not func["is_dependency"] else 0.7
            all_results.append(func)
        
        for cls in results["classes_by_name"]:
            cls["search_type"] = "class_name"
            cls["relevance_score"] = 0.8 if not cls["is_dependency"] else 0.6
            all_results.append(cls)

        for var in results["variables_by_name"]:
            var["search_type"] = "variable_name"
            var["relevance_score"] = 0.7 if not var["is_dependency"] else 0.5
            all_results.append(var)
        
        for content in results["content_matches"]:
            content["search_type"] = "content"
            content["relevance_score"] = 0.6 if not content["is_dependency"] else 0.4
            all_results.append(content)
        
        all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        results["ranked_results"] = all_results[:15]
        results["total_matches"] = len(all_results)
        
        return results
    
    def find_functions_by_argument(self, argument_name: str, file_path: str = None) -> List[Dict]:
        """Find functions that take a specific argument name."""
        with self.driver.session() as session:
            if file_path:
                query = """
                    MATCH (f:Function)-[:HAS_PARAMETER]->(p:Parameter)
                    WHERE p.name = $argument_name AND f.file_path = $file_path
                    RETURN f.name AS function_name, f.file_path AS file_path, f.line_number AS line_number,
                           f.docstring AS docstring, f.is_dependency AS is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 20
                """
                result = session.run(query, argument_name=argument_name, file_path=file_path)
            else:
                query = """
                    MATCH (f:Function)-[:HAS_PARAMETER]->(p:Parameter)
                    WHERE p.name = $argument_name
                    RETURN f.name AS function_name, f.file_path AS file_path, f.line_number AS line_number,
                           f.docstring AS docstring, f.is_dependency AS is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 20
                """
                result = session.run(query, argument_name=argument_name)
            return [dict(record) for record in result]

    def find_functions_by_decorator(self, decorator_name: str, file_path: str = None) -> List[Dict]:
        """Find functions that have a specific decorator applied to them."""
        with self.driver.session() as session:
            if file_path:
                query = """
                    MATCH (f:Function)
                    WHERE f.file_path = $file_path AND $decorator_name IN f.decorators
                    RETURN f.name AS function_name, f.file_path AS file_path, f.line_number AS line_number,
                           f.docstring AS docstring, f.is_dependency AS is_dependency, f.decorators AS decorators
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 20
                """
                result = session.run(query, decorator_name=decorator_name, file_path=file_path)
            else:
                query = """
                    MATCH (f:Function)
                    WHERE $decorator_name IN f.decorators
                    RETURN f.name AS function_name, f.file_path AS file_path, f.line_number AS line_number,
                           f.docstring AS docstring, f.is_dependency AS is_dependency, f.decorators AS decorators
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 20
                """
                result = session.run(query, decorator_name=decorator_name)
            return [dict(record) for record in result]
    
    def who_calls_function(self, function_name: str, file_path: str = None) -> List[Dict]:
        """Find what functions call a specific function using CALLS relationships with improved matching"""
        with self.driver.session() as session:
            if file_path:
                result = session.run("""
                    MATCH (caller:Function)-[call:CALLS]->(target:Function {name: $function_name, file_path: $file_path})
                    OPTIONAL MATCH (caller_file:File)-[:CONTAINS]->(caller)
                    RETURN DISTINCT
                        caller.name as caller_function,
                        caller.file_path as caller_file_path,
                        caller.line_number as caller_line_number,
                        caller.docstring as caller_docstring,
                        caller.is_dependency as caller_is_dependency,
                        call.line_number as call_line_number,
                        call.args as call_args,
                        call.full_call_name as full_call_name,
                        call.call_type as call_type,
                        target.file_path as target_file_path
                    ORDER BY caller.is_dependency ASC, caller.file_path, caller.line_number
                    LIMIT 20
                """, function_name=function_name, file_path=file_path)
                
                results = [dict(record) for record in result]
                if not results:
                    result = session.run("""
                        MATCH (target:Function {name: $function_name})
                        MATCH (caller:Function)-[call:CALLS]->(target)
                        OPTIONAL MATCH (caller_file:File)-[:CONTAINS]->(caller)
                        RETURN DISTINCT
                            caller.name as caller_function,
                            caller.file_path as caller_file_path,
                            caller.line_number as caller_line_number,
                            caller.docstring as caller_docstring,
                            caller.is_dependency as caller_is_dependency,
                            call.line_number as call_line_number,
                            call.args as call_args,
                            call.full_call_name as full_call_name,
                            call.call_type as call_type,
                            target.file_path as target_file_path
                        ORDER BY caller.is_dependency ASC, caller.file_path, caller.line_number
                        LIMIT 20
                    """, function_name=function_name)
                    results = [dict(record) for record in result]
            else:
                result = session.run("""
                    MATCH (target:Function {name: $function_name})
                    MATCH (caller:Function)-[call:CALLS]->(target)
                    OPTIONAL MATCH (caller_file:File)-[:CONTAINS]->(caller)
                    RETURN DISTINCT
                        caller.name as caller_function,
                        caller.file_path as caller_file_path,
                        caller.line_number as caller_line_number,
                        caller.docstring as caller_docstring,
                        caller.is_dependency as caller_is_dependency,
                        call.line_number as call_line_number,
                        call.args as call_args,
                        call.full_call_name as full_call_name,
                        call.call_type as call_type,
                        target.file_path as target_file_path
                    ORDER BY caller.is_dependency ASC, caller.file_path, caller.line_number
                    LIMIT 20
                """, function_name=function_name)
                results = [dict(record) for record in result]
            
            return results
    
    def what_does_function_call(self, function_name: str, file_path: str = None) -> List[Dict]:
        """Find what functions a specific function calls using CALLS relationships"""
        with self.driver.session() as session:
            if file_path:
                # Convert file_path to absolute path
                absolute_file_path = str(Path(file_path).resolve())
                result = session.run("""
                    MATCH (caller:Function {name: $function_name, file_path: $absolute_file_path})
                    MATCH (caller)-[call:CALLS]->(called:Function)
                    OPTIONAL MATCH (called_file:File)-[:CONTAINS]->(called)
                    RETURN DISTINCT
                        called.name as called_function,
                        called.file_path as called_file_path,
                        called.line_number as called_line_number,
                        called.docstring as called_docstring,
                        called.is_dependency as called_is_dependency,
                        call.line_number as call_line_number,
                        call.args as call_args,
                        call.full_call_name as full_call_name,
                        call.call_type as call_type
                    ORDER BY called.is_dependency ASC, called.name
                    LIMIT 20
                """, function_name=function_name, absolute_file_path=absolute_file_path)
            else:
                result = session.run("""
                    MATCH (caller:Function {name: $function_name})
                    MATCH (caller)-[call:CALLS]->(called:Function)
                    OPTIONAL MATCH (called_file:File)-[:CONTAINS]->(called)
                    RETURN DISTINCT
                        called.name as called_function,
                        called.file_path as called_file_path,
                        called.line_number as called_line_number,
                        called.docstring as called_docstring,
                        called.is_dependency as called_is_dependency,
                        call.line_number as call_line_number,
                        call.args as call_args,
                        call.full_call_name as full_call_name,
                        call.call_type as call_type
                    ORDER BY called.is_dependency ASC, called.name
                    LIMIT 20
                """, function_name=function_name)
            
            return [dict(record) for record in result]
    
    def who_imports_module(self, module_name: str) -> List[Dict]:
        """Find what files import a specific module using IMPORTS relationships"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (file:File)-[imp:IMPORTS]->(module:Module)
                WHERE module.name = $module_name OR module.full_import_name CONTAINS $module_name
                OPTIONAL MATCH (repo:Repository)-[:CONTAINS]->(file)
                WITH file, repo, COLLECT({
                    imported_module: module.name,
                    import_alias: module.alias,
                    full_import_name: module.full_import_name
                }) AS imports
                RETURN
                    file.name AS file_name,
                    file.path AS file_path,
                    file.relative_path AS file_relative_path,
                    file.is_dependency AS file_is_dependency,
                    repo.name AS repository_name,
                    imports
                ORDER BY file.is_dependency ASC, file.path
                LIMIT 20
            """, module_name=module_name)
            
            return [dict(record) for record in result]
    
    def who_modifies_variable(self, variable_name: str) -> List[Dict]:
        """Find what functions contain or modify a specific variable"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (var:Variable {name: $variable_name})
                MATCH (container)-[:CONTAINS]->(var)
                WHERE container:Function OR container:Class OR container:File
                OPTIONAL MATCH (file:File)-[:CONTAINS]->(container)
                RETURN DISTINCT
                    CASE 
                        WHEN container:Function THEN container.name
                        WHEN container:Class THEN container.name
                        ELSE 'file_level'
                    END as container_name,
                    CASE 
                        WHEN container:Function THEN 'function'
                        WHEN container:Class THEN 'class'
                        ELSE 'file'
                    END as container_type,
                    COALESCE(container.file_path, file.path) as file_path,
                    container.line_number as container_line_number,
                    var.line_number as variable_line_number,
                    var.value as variable_value,
                    var.context as variable_context,
                    COALESCE(container.is_dependency, file.is_dependency, false) as is_dependency
                ORDER BY is_dependency ASC, file_path, variable_line_number
                LIMIT 20
            """, variable_name=variable_name)
            
            return [dict(record) for record in result]
    
    def find_class_hierarchy(self, class_name: str, file_path: str = None) -> Dict[str, Any]:
        """Find class inheritance relationships using INHERITS relationships"""
        with self.driver.session() as session:
            if file_path:
                match_clause = "MATCH (child:Class {name: $class_name, file_path: $file_path})"
            else:
                match_clause = "MATCH (child:Class {name: $class_name})"

            parents_query = f"""
                {match_clause}
                MATCH (child)-[:INHERITS]->(parent:Class)
                OPTIONAL MATCH (parent_file:File)-[:CONTAINS]->(parent)
                RETURN DISTINCT
                    parent.name as parent_class,
                    parent.file_path as parent_file_path,
                    parent.line_number as parent_line_number,
                    parent.docstring as parent_docstring,
                    parent.is_dependency as parent_is_dependency
                ORDER BY parent.is_dependency ASC, parent.name
            """
            parents_result = session.run(parents_query, class_name=class_name, file_path=file_path)
            
            children_query = f"""
                {match_clause}
                MATCH (grandchild:Class)-[:INHERITS]->(child)
                OPTIONAL MATCH (child_file:File)-[:CONTAINS]->(grandchild)
                RETURN DISTINCT
                    grandchild.name as child_class,
                    grandchild.file_path as child_file_path,
                    grandchild.line_number as child_line_number,
                    grandchild.docstring as child_docstring,
                    grandchild.is_dependency as child_is_dependency
                ORDER BY grandchild.is_dependency ASC, grandchild.name
            """
            children_result = session.run(children_query, class_name=class_name, file_path=file_path)
            
            methods_query = f"""
                {match_clause}
                MATCH (child)-[:CONTAINS]->(method:Function)
                RETURN DISTINCT
                    method.name as method_name,
                    method.file_path as method_file_path,
                    method.line_number as method_line_number,
                    method.args as method_args,
                    method.docstring as method_docstring,
                    method.is_dependency as method_is_dependency
                ORDER BY method.is_dependency ASC, method.line_number
            """
            methods_result = session.run(methods_query, class_name=class_name, file_path=file_path)
            
            return {
                "class_name": class_name,
                "parent_classes": [dict(record) for record in parents_result],
                "child_classes": [dict(record) for record in children_result],
                "methods": [dict(record) for record in methods_result]
            }
    
    def find_function_overrides(self, function_name: str) -> List[Dict]:
        """Find all implementations of a function across different classes"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (class:Class)-[:CONTAINS]->(func:Function {name: $function_name})
                OPTIONAL MATCH (file:File)-[:CONTAINS]->(class)
                RETURN DISTINCT
                    class.name as class_name,
                    class.file_path as class_file_path,
                    func.name as function_name,
                    func.line_number as function_line_number,
                    func.args as function_args,
                    func.docstring as function_docstring,
                    func.is_dependency as is_dependency,
                    file.name as file_name
                ORDER BY func.is_dependency ASC, class.name
                LIMIT 20
            """, function_name=function_name)
            
            return [dict(record) for record in result]
    
    def find_dead_code(self, exclude_decorated_with: List[str] = None) -> Dict[str, Any]:
        """Find potentially unused functions (not called by other functions in the project), optionally excluding those with specific decorators."""
        if exclude_decorated_with is None:
            exclude_decorated_with = []

        with self.driver.session() as session:
            result = session.run("""
                MATCH (func:Function)
                WHERE func.is_dependency = false
                  AND NOT func.name IN ['main', '__init__', '__main__', 'setup', 'run', '__new__', '__del__']
                  AND NOT func.name STARTS WITH '_test'
                  AND NOT func.name STARTS WITH 'test_'
                  AND ALL(decorator_name IN $exclude_decorated_with WHERE NOT decorator_name IN func.decorators)
                WITH func
                OPTIONAL MATCH (caller:Function)-[:CALLS]->(func)
                WHERE caller.is_dependency = false
                WITH func, count(caller) as caller_count
                WHERE caller_count = 0
                OPTIONAL MATCH (file:File)-[:CONTAINS]->(func)
                RETURN
                    func.name as function_name,
                    func.file_path as file_path,
                    func.line_number as line_number,
                    func.docstring as docstring,
                    func.context as context,
                    file.name as file_name
                ORDER BY func.file_path, func.line_number
                LIMIT 50
            """, exclude_decorated_with=exclude_decorated_with)
            
            return {
                "potentially_unused_functions": [dict(record) for record in result],
                "note": "These functions might be unused, but could be entry points, callbacks, or called dynamically"
            }
    
    def find_all_callers(self, function_name: str, file_path: str = None) -> List[Dict]:
        """Find all direct and indirect callers of a specific function."""
        with self.driver.session() as session:
            if file_path:
                # Find functions within the specified file_path that call the target function
                query = """
                    MATCH (f:Function)-[:CALLS*]->(target:Function {name: $function_name, file_path: $file_path})
                    RETURN DISTINCT f.name AS caller_name, f.file_path AS caller_file_path, f.line_number AS caller_line_number, f.is_dependency AS caller_is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 50
                """
                result = session.run(query, function_name=function_name, file_path=file_path)
            else:
                # If no file_path (context) is provided, find all callers of the function by name
                query = """
                    MATCH (f:Function)-[:CALLS*]->(target:Function {name: $function_name})
                    RETURN DISTINCT f.name AS caller_name, f.file_path AS caller_file_path, f.line_number AS caller_line_number, f.is_dependency AS caller_is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 50
                """
                result = session.run(query, function_name=function_name)
            return [dict(record) for record in result]

    def find_all_callees(self, function_name: str, file_path: str = None) -> List[Dict]:
        """Find all direct and indirect callees of a specific function."""
        with self.driver.session() as session:
            if file_path:
                query = """
                    MATCH (caller:Function {name: $function_name, file_path: $file_path})
                    MATCH (caller)-[:CALLS*]->(f:Function)
                    RETURN DISTINCT f.name AS callee_name, f.file_path AS callee_file_path, f.line_number AS callee_line_number, f.is_dependency AS callee_is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 50
                """
                result = session.run(query, function_name=function_name, file_path=file_path)
            else:
                query = """
                    MATCH (caller:Function {name: $function_name})
                    MATCH (caller)-[:CALLS*]->(f:Function)
                    RETURN DISTINCT f.name AS callee_name, f.file_path AS callee_file_path, f.line_number AS callee_line_number, f.is_dependency AS callee_is_dependency
                    ORDER BY f.is_dependency ASC, f.file_path, f.line_number
                    LIMIT 50
                """
                result = session.run(query, function_name=function_name)
            return [dict(record) for record in result]

    def find_function_call_chain(self, start_function: str, end_function: str, max_depth: int = 5) -> List[Dict]:
        """Find call chains between two functions"""
        with self.driver.session() as session:
            result = session.run(f"""
                MATCH path = shortestPath(
                    (start:Function {{name: $start_function}})-[:CALLS*1..{max_depth}]->(end:Function {{name: $end_function}})
                )
                WITH path, nodes(path) as func_nodes, relationships(path) as call_rels
                RETURN 
                    [node in func_nodes | {{
                        name: node.name,
                        file_path: node.file_path,
                        line_number: node.line_number,
                        is_dependency: node.is_dependency
                    }}] as function_chain,
                    [rel in call_rels | {{
                        call_line: rel.line_number,
                        args: rel.args,
                        full_call_name: rel.full_call_name
                    }}] as call_details,
                    length(path) as chain_length
                ORDER BY chain_length ASC
                LIMIT 10
            """, start_function=start_function, end_function=end_function)
            
            return [dict(record) for record in result]
    
    def find_module_dependencies(self, module_name: str) -> Dict[str, Any]:
        """Find all dependencies and dependents of a module"""
        with self.driver.session() as session:
            importers_result = session.run("""
                MATCH (file:File)-[:IMPORTS]->(module:Module {name: $module_name})
                OPTIONAL MATCH (repo:Repository)-[:CONTAINS]->(file)
                RETURN DISTINCT
                    file.name as file_name,
                    file.path as file_path,
                    file.is_dependency as file_is_dependency,
                    repo.name as repository_name
                ORDER BY file.is_dependency ASC, file.path
                LIMIT 20
            """, module_name=module_name)
            
            related_imports_result = session.run("""
                MATCH (file:File)-[:IMPORTS]->(target_module:Module {name: $module_name})
                MATCH (file)-[:IMPORTS]->(other_module:Module)
                WHERE other_module <> target_module
                RETURN DISTINCT
                    other_module.name as related_module,
                    other_module.alias as module_alias,
                    count(file) as usage_count
                ORDER BY usage_count DESC
                LIMIT 20
            """, module_name=module_name)
            
            return {
                "module_name": module_name,
                "imported_by_files": [dict(record) for record in importers_result],
                "frequently_used_with": [dict(record) for record in related_imports_result]
            }
    
    def find_variable_usage_scope(self, variable_name: str) -> Dict[str, Any]:
        """Find the scope and usage patterns of a variable"""
        with self.driver.session() as session:
            variable_instances = session.run("""
                MATCH (var:Variable {name: $variable_name})
                OPTIONAL MATCH (container)-[:CONTAINS]->(var)
                WHERE container:Function OR container:Class OR container:File
                OPTIONAL MATCH (file:File)-[:CONTAINS]->(var)
                RETURN DISTINCT
                    var.name as variable_name,
                    var.value as variable_value,
                    var.line_number as line_number,
                    var.context as context,
                    COALESCE(var.file_path, file.path) as file_path,
                    CASE 
                        WHEN container:Function THEN 'function'
                        WHEN container:Class THEN 'class'
                        ELSE 'module'
                    END as scope_type,
                    CASE 
                        WHEN container:Function THEN container.name
                        WHEN container:Class THEN container.name
                        ELSE 'module_level'
                    END as scope_name,
                    var.is_dependency as is_dependency
                ORDER BY var.is_dependency ASC, file_path, line_number
            """, variable_name=variable_name)
            
            return {
                "variable_name": variable_name,
                "instances": [dict(record) for record in variable_instances]
            }
    
    def analyze_code_relationships(self, query_type: str, target: str, context: str = None) -> Dict[str, Any]:
        """Main method to analyze different types of code relationships with fixed return types"""
        query_type = query_type.lower().strip()
        
        try:
            if query_type == "find_callers":
                results = self.who_calls_function(target, context)
                return {
                    "query_type": "find_callers", "target": target, "context": context, "results": results,
                    "summary": f"Found {len(results)} functions that call '{target}'"
                }
            
            elif query_type == "find_callees":
                results = self.what_does_function_call(target, context)
                return {
                    "query_type": "find_callees", "target": target, "context": context, "results": results,
                    "summary": f"Function '{target}' calls {len(results)} other functions"
                }
                
            elif query_type == "find_importers":
                results = self.who_imports_module(target)
                return {
                    "query_type": "find_importers", "target": target, "results": results,
                    "summary": f"Found {len(results)} files that import '{target}'"
                }
                
            elif query_type == "find_functions_by_argument":
                results = self.find_functions_by_argument(target, context)
                return {
                    "query_type": "find_functions_by_argument", "target": target, "context": context, "results": results,
                    "summary": f"Found {len(results)} functions that take '{target}' as an argument"
                }
            
            elif query_type == "find_functions_by_decorator":
                results = self.find_functions_by_decorator(target, context)
                return {
                    "query_type": "find_functions_by_decorator", "target": target, "context": context, "results": results,
                    "summary": f"Found {len(results)} functions decorated with '{target}'"
                }
                
            elif query_type in ["who_modifies", "modifies", "mutations", "changes", "variable_usage"]:
                results = self.who_modifies_variable(target)
                return {
                    "query_type": "who_modifies", "target": target, "results": results,
                    "summary": f"Found {len(results)} containers that hold variable '{target}'"
                }
            
            elif query_type in ["class_hierarchy", "inheritance", "extends"]:
                results = self.find_class_hierarchy(target, context)
                return {
                    "query_type": "class_hierarchy", "target": target, "results": results,
                    "summary": f"Class '{target}' has {len(results['parent_classes'])} parents, {len(results['child_classes'])} children, and {len(results['methods'])} methods"
                }
            
            elif query_type in ["overrides", "implementations", "polymorphism"]:
                results = self.find_function_overrides(target)
                return {
                    "query_type": "overrides", "target": target, "results": results,
                    "summary": f"Found {len(results)} implementations of function '{target}'"
                }
            
            elif query_type in ["dead_code", "unused", "unreachable"]:
                results = self.find_dead_code()
                return {
                    "query_type": "dead_code", "results": results,
                    "summary": f"Found {len(results['potentially_unused_functions'])} potentially unused functions"
                }
            
            elif query_type == "find_complexity":
                limit = int(context) if context and context.isdigit() else 10
                results = self.find_most_complex_functions(limit)
                return {
                    "query_type": "find_complexity", "limit": limit, "results": results,
                    "summary": f"Found the top {len(results)} most complex functions"
                }
            
            elif query_type == "find_all_callers":
                results = self.find_all_callers(target, context)
                return {
                    "query_type": "find_all_callers", "target": target, "context": context, "results": results,
                    "summary": f"Found {len(results)} direct and indirect callers of '{target}'"
                }

            elif query_type == "find_all_callees":
                results = self.find_all_callees(target, context)
                return {
                    "query_type": "find_all_callees", "target": target, "context": context, "results": results,
                    "summary": f"Found {len(results)} direct and indirect callees of '{target}'"
                }
                
            elif query_type in ["call_chain", "path", "chain"]:
                if '->' in target:
                    start_func, end_func = target.split('->', 1)
                    # max_depth can be passed as context, default to 5 if not provided or invalid
                    max_depth = int(context) if context and context.isdigit() else 5
                    results = self.find_function_call_chain(start_func.strip(), end_func.strip(), max_depth)
                    return {
                        "query_type": "call_chain", "target": target, "results": results,
                        "summary": f"Found {len(results)} call chains from '{start_func.strip()}' to '{end_func.strip()}' (max depth: {max_depth})"
                    }
                else:
                    return {
                        "error": "For call_chain queries, use format 'start_function->end_function'",
                        "example": "main->process_data"
                    }
            
            elif query_type in ["module_deps", "module_dependencies", "module_usage"]:
                results = self.find_module_dependencies(target)
                return {
                    "query_type": "module_dependencies", "target": target, "results": results,
                    "summary": f"Module '{target}' is imported by {len(results['imported_by_files'])} files"
                }
            
            elif query_type in ["variable_scope", "var_scope", "variable_usage_scope"]:
                results = self.find_variable_usage_scope(target)
                return {
                    "query_type": "variable_scope", "target": target, "results": results,
                    "summary": f"Variable '{target}' has {len(results['instances'])} instances across different scopes"
                }
            
            else:
                return {
                    "error": f"Unknown query type: {query_type}",
                    "supported_types": [
                        "find_callers", "find_callees", "find_importers", "who_modifies",
                        "class_hierarchy", "overrides", "dead_code", "call_chain",
                        "module_deps", "variable_scope", "find_complexity"
                    ]
                }
        
        except Exception as e:
            return {
                "error": f"Error executing relationship query: {str(e)}",
                "query_type": query_type,
                "target": target
            }

    def get_cyclomatic_complexity(self, function_name: str, file_path: str = None) -> List[Dict]:
        """Get the cyclomatic complexity of a function."""
        with self.driver.session() as session:
            if file_path:
                # Use ENDS WITH for flexible path matching
                query = """
                    MATCH (f:Function {name: $function_name})
                    WHERE f.file_path ENDS WITH $file_path
                    RETURN f.name as function_name, f.file_path as file_path, f.cyclomatic_complexity as complexity
                """
                result = session.run(query, function_name=function_name, file_path=file_path)
            else:
                query = """
                    MATCH (f:Function {name: $function_name})
                    RETURN f.name as function_name, f.file_path as file_path, f.cyclomatic_complexity as complexity
                """
                result = session.run(query, function_name=function_name)
            
            return [dict(record) for record in result]

    def find_most_complex_functions(self, limit: int = 10) -> List[Dict]:
        """Find the most complex functions based on cyclomatic complexity."""
        with self.driver.session() as session:
            query = """
                MATCH (f:Function)
                WHERE f.cyclomatic_complexity IS NOT NULL AND f.is_dependency = false
                RETURN f.name as function_name, f.file_path as file_path, f.cyclomatic_complexity as complexity, f.line_number as line_number
                ORDER BY f.cyclomatic_complexity DESC
                LIMIT $limit
            """
            result = session.run(query, limit=limit)
            return [dict(record) for record in result]

    def list_indexed_repositories(self) -> List[Dict]:
        """List all indexed repositories."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (r:Repository)
                RETURN r.name as name, r.path as path, r.is_dependency as is_dependency
                ORDER BY r.name
            """)
            return [dict(record) for record in result]

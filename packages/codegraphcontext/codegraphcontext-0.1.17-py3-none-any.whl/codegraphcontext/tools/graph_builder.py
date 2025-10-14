
# src/codegraphcontext/tools/graph_builder.py
import asyncio
import pathspec
from pathlib import Path
from typing import Any, Coroutine, Dict, Optional, Tuple
from datetime import datetime

from ..core.database import DatabaseManager
from ..core.jobs import JobManager, JobStatus
from ..utils.debug_log import debug_log, info_logger, error_logger, warning_logger

# New imports for tree-sitter
from tree_sitter import Language, Parser
from tree_sitter_languages import get_language

class TreeSitterParser:
    """A generic parser wrapper for a specific language using tree-sitter."""

    def __init__(self, language_name: str):
        self.language_name = language_name
        self.language: Language = get_language(language_name)
        self.parser = Parser()
        self.parser.set_language(self.language)

        self.language_specific_parser = None
        if self.language_name == 'python':
            from .languages.python import PythonTreeSitterParser
            self.language_specific_parser = PythonTreeSitterParser(self)
        elif self.language_name == 'javascript':
            from .languages.javascript import JavascriptTreeSitterParser
            self.language_specific_parser = JavascriptTreeSitterParser(self)
        elif self.language_name == 'go':
             from .languages.go import GoTreeSitterParser
             self.language_specific_parser = GoTreeSitterParser(self)
        elif self.language_name == 'typescript':
            from .languages.typescript import TypescriptTreeSitterParser
            self.language_specific_parser = TypescriptTreeSitterParser(self)
        elif self.language_name == 'cpp':
            from .languages.cpp import CppTreeSitterParser
            self.language_specific_parser = CppTreeSitterParser(self)
        elif self.language_name == 'rust':
            from .languages.rust import RustTreeSitterParser
            self.language_specific_parser = RustTreeSitterParser(self)
        elif self.language_name == 'c':
            from .languages.c import CTreeSitterParser
            self.language_specific_parser = CTreeSitterParser(self)
        elif self.language_name == 'java':
            from .languages.java import JavaTreeSitterParser
            self.language_specific_parser = JavaTreeSitterParser(self)
        elif self.language_name == 'ruby':
            from .languages.ruby import RubyTreeSitterParser
            self.language_specific_parser = RubyTreeSitterParser(self)


    def parse(self, file_path: Path, is_dependency: bool = False, **kwargs) -> Dict:
        """Dispatches parsing to the language-specific parser."""
        if self.language_specific_parser:
            return self.language_specific_parser.parse(file_path, is_dependency, **kwargs)
        else:
            raise NotImplementedError(f"No language-specific parser implemented for {self.language_name}")

class GraphBuilder:
    """Module for building and managing the Neo4j code graph."""

    def __init__(self, db_manager: DatabaseManager, job_manager: JobManager, loop: asyncio.AbstractEventLoop):
        self.db_manager = db_manager
        self.job_manager = job_manager
        self.loop = loop
        self.driver = self.db_manager.get_driver()
        self.parsers = {
            '.py': TreeSitterParser('python'),
            '.ipynb': TreeSitterParser('python'),
            '.js': TreeSitterParser('javascript'),
            '.jsx': TreeSitterParser('javascript'),
            '.mjs': TreeSitterParser('javascript'),
            '.cjs': TreeSitterParser('javascript'),
            '.go': TreeSitterParser('go'),
            '.ts': TreeSitterParser('typescript'),
            '.tsx': TreeSitterParser('typescript'),
            '.cpp': TreeSitterParser('cpp'),
            '.h': TreeSitterParser('cpp'),
            '.hpp': TreeSitterParser('cpp'),
            '.rs': TreeSitterParser('rust'),
            '.c': TreeSitterParser('c'),
            # '.h': TreeSitterParser('c'), # Need to write an algo for distinguishing C vs C++ headers
            '.java': TreeSitterParser('java'),
            '.rb': TreeSitterParser('ruby')
        }
        self.create_schema()

    # A general schema creation based on common features across languages
    def create_schema(self):
        """Create constraints and indexes in Neo4j."""
        # When adding a new node type with a unique key, add its constraint here.
        with self.driver.session() as session:
            try:
                session.run("CREATE CONSTRAINT repository_path IF NOT EXISTS FOR (r:Repository) REQUIRE r.path IS UNIQUE")
                session.run("CREATE CONSTRAINT file_path IF NOT EXISTS FOR (f:File) REQUIRE f.path IS UNIQUE")
                session.run("CREATE CONSTRAINT directory_path IF NOT EXISTS FOR (d:Directory) REQUIRE d.path IS UNIQUE")
                session.run("CREATE CONSTRAINT function_unique IF NOT EXISTS FOR (f:Function) REQUIRE (f.name, f.file_path, f.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT class_unique IF NOT EXISTS FOR (c:Class) REQUIRE (c.name, c.file_path, c.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT trait_unique IF NOT EXISTS FOR (t:Trait) REQUIRE (t.name, t.file_path, t.line_number) IS UNIQUE") # Added trait constraint
                session.run("CREATE CONSTRAINT interface_unique IF NOT EXISTS FOR (i:Interface) REQUIRE (i.name, i.file_path, i.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT macro_unique IF NOT EXISTS FOR (m:Macro) REQUIRE (m.name, m.file_path, m.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT variable_unique IF NOT EXISTS FOR (v:Variable) REQUIRE (v.name, v.file_path, v.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT module_name IF NOT EXISTS FOR (m:Module) REQUIRE m.name IS UNIQUE")
                session.run("CREATE CONSTRAINT struct_cpp IF NOT EXISTS FOR (cstruct: Struct) REQUIRE (cstruct.name, cstruct.file_path, cstruct.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT enum_cpp IF NOT EXISTS FOR (cenum: Enum) REQUIRE (cenum.name, cenum.file_path, cenum.line_number) IS UNIQUE")
                session.run("CREATE CONSTRAINT union_cpp IF NOT EXISTS FOR (cunion: Union) REQUIRE (cunion.name, cunion.file_path, cunion.line_number) IS UNIQUE")

                
                # Indexes for language attribute
                session.run("CREATE INDEX function_lang IF NOT EXISTS FOR (f:Function) ON (f.lang)")
                session.run("CREATE INDEX class_lang IF NOT EXISTS FOR (c:Class) ON (c.lang)")
                
                session.run("""
                    CREATE FULLTEXT INDEX code_search_index IF NOT EXISTS 
                    FOR (n:Function|Class|Variable) 
                    ON EACH [n.name, n.source, n.docstring]
                """ )
                
                info_logger("Database schema verified/created successfully")
            except Exception as e:
                warning_logger(f"Schema creation warning: {e}")


    def _pre_scan_for_imports(self, files: list[Path]) -> dict:
        """Dispatches pre-scan to the correct language-specific implementation."""
        imports_map = {}
        
        # Group files by language/extension
        files_by_lang = {}
        for file in files:
            if file.suffix in self.parsers:
                lang_ext = file.suffix
                if lang_ext not in files_by_lang:
                    files_by_lang[lang_ext] = []
                files_by_lang[lang_ext].append(file)

        if '.py' in files_by_lang:
            from .languages import python as python_lang_module
            imports_map.update(python_lang_module.pre_scan_python(files_by_lang['.py'], self.parsers['.py']))
        elif '.ipynb' in files_by_lang:
            from .languages import python as python_lang_module
            imports_map.update(python_lang_module.pre_scan_python(files_by_lang['.ipynb'], self.parsers['.ipynb']))
        elif '.js' in files_by_lang:
            from .languages import javascript as js_lang_module
            imports_map.update(js_lang_module.pre_scan_javascript(files_by_lang['.js'], self.parsers['.js']))
        elif '.jsx' in files_by_lang:
            from .languages import javascript as js_lang_module
            imports_map.update(js_lang_module.pre_scan_javascript(files_by_lang['.jsx'], self.parsers['.jsx']))
        elif '.mjs' in files_by_lang:
            from .languages import javascript as js_lang_module
            imports_map.update(js_lang_module.pre_scan_javascript(files_by_lang['.mjs'], self.parsers['.mjs']))
        elif '.cjs' in files_by_lang:
            from .languages import javascript as js_lang_module
            imports_map.update(js_lang_module.pre_scan_javascript(files_by_lang['.cjs'], self.parsers['.cjs']))
        elif '.go' in files_by_lang:
             from .languages import go as go_lang_module
             imports_map.update(go_lang_module.pre_scan_go(files_by_lang['.go'], self.parsers['.go']))
        elif '.ts' in files_by_lang:
            from .languages import typescript as ts_lang_module
            imports_map.update(ts_lang_module.pre_scan_typescript(files_by_lang['.ts'], self.parsers['.ts']))
        elif '.tsx' in files_by_lang:
            from .languages import typescript as ts_lang_module
            imports_map.update(ts_lang_module.pre_scan_typescript(files_by_lang['.tsx'], self.parsers['.tsx']))
        elif '.cpp' in files_by_lang:
            from .languages import cpp as cpp_lang_module
            imports_map.update(cpp_lang_module.pre_scan_cpp(files_by_lang['.cpp'], self.parsers['.cpp']))
        elif '.h' in files_by_lang:
            from .languages import cpp as cpp_lang_module
            imports_map.update(cpp_lang_module.pre_scan_cpp(files_by_lang['.h'], self.parsers['.h']))
        elif '.hpp' in files_by_lang:
            from .languages import cpp as cpp_lang_module
            imports_map.update(cpp_lang_module.pre_scan_cpp(files_by_lang['.hpp'], self.parsers['.hpp']))
        elif '.rs' in files_by_lang:
            from .languages import rust as rust_lang_module
            imports_map.update(rust_lang_module.pre_scan_rust(files_by_lang['.rs'], self.parsers['.rs']))
        elif '.c' in files_by_lang:
            from .languages import c as c_lang_module
            imports_map.update(c_lang_module.pre_scan_c(files_by_lang['.c'], self.parsers['.c']))
        elif '.java' in files_by_lang:
            from .languages import java as java_lang_module
            imports_map.update(java_lang_module.pre_scan_java(files_by_lang['.java'], self.parsers['.java']))
        elif '.rb' in files_by_lang:
            from .languages import ruby as ruby_lang_module
            imports_map.update(ruby_lang_module.pre_scan_ruby(files_by_lang['.rb'], self.parsers['.rb']))
            
        return imports_map

    # Language-agnostic method
    def add_repository_to_graph(self, repo_path: Path, is_dependency: bool = False):
        """Adds a repository node using its absolute path as the unique key."""
        repo_name = repo_path.name
        repo_path_str = str(repo_path.resolve())
        with self.driver.session() as session:
            session.run(
                """
                MERGE (r:Repository {path: $path})
                SET r.name = $name, r.is_dependency = $is_dependency
                """,
                path=repo_path_str,
                name=repo_name,
                is_dependency=is_dependency,
            )

    # First pass to add file and its contents
    def add_file_to_graph(self, file_data: Dict, repo_name: str, imports_map: dict):
        info_logger("Executing add_file_to_graph with my change!")
        """Adds a file and its contents within a single, unified session."""
        file_path_str = str(Path(file_data['file_path']).resolve())
        file_name = Path(file_path_str).name
        is_dependency = file_data.get('is_dependency', False)

        with self.driver.session() as session:
            try:
                # Match repository by path, not name, to avoid conflicts with same-named folders at different locations
                repo_result = session.run("MATCH (r:Repository {path: $repo_path}) RETURN r.path as path", repo_path=str(Path(file_data['repo_path']).resolve())).single()
                relative_path = str(Path(file_path_str).relative_to(Path(repo_result['path']))) if repo_result else file_name
            except ValueError:
                relative_path = file_name

            session.run("""
                MERGE (f:File {path: $path})
                SET f.name = $name, f.relative_path = $relative_path, f.is_dependency = $is_dependency
            """, path=file_path_str, name=file_name, relative_path=relative_path, is_dependency=is_dependency)

            file_path_obj = Path(file_path_str)
            repo_path_obj = Path(repo_result['path'])
            
            relative_path_to_file = file_path_obj.relative_to(repo_path_obj)
            
            parent_path = str(repo_path_obj)
            parent_label = 'Repository'

            for part in relative_path_to_file.parts[:-1]:
                current_path = Path(parent_path) / part
                current_path_str = str(current_path)
                
                session.run(f"""
                    MATCH (p:{parent_label} {{path: $parent_path}})
                    MERGE (d:Directory {{path: $current_path}})
                    SET d.name = $part
                    MERGE (p)-[:CONTAINS]->(d)
                """, parent_path=parent_path, current_path=current_path_str, part=part)

                parent_path = current_path_str
                parent_label = 'Directory'

            session.run(f"""
                MATCH (p:{parent_label} {{path: $parent_path}})
                MATCH (f:File {{path: $file_path}})
                MERGE (p)-[:CONTAINS]->(f)
            """, parent_path=parent_path, file_path=file_path_str)

            # CONTAINS relationships for functions, classes, and variables
            # To add a new language-specific node type (e.g., 'Trait' for Rust):
            # 1. Ensure your language-specific parser returns a list under a unique key (e.g., 'traits': [...] ).
            # 2. Add a new constraint for the new label in the `create_schema` method.
            # 3. Add a new entry to the `item_mappings` list below (e.g., (file_data.get('traits', []), 'Trait') ).
            item_mappings = [
                (file_data.get('functions', []), 'Function'),
                (file_data.get('classes', []), 'Class'),
                (file_data.get('traits', []), 'Trait'), # <-- Added trait mapping
                (file_data.get('variables', []), 'Variable'),
                (file_data.get('interfaces', []), 'Interface'),
                (file_data.get('macros', []), 'Macro'),
                (file_data.get('structs',[]), 'Struct'),
                (file_data.get('enums',[]), 'Enum'),
                (file_data.get('unions',[]), 'Union'),
            ]
            for item_data, label in item_mappings:
                for item in item_data:
                    # Ensure cyclomatic_complexity is set for functions
                    if label == 'Function' and 'cyclomatic_complexity' not in item:
                        item['cyclomatic_complexity'] = 1 # Default value

                    query = f"""
                        MATCH (f:File {{path: $file_path}})
                        MERGE (n:{label} {{name: $name, file_path: $file_path, line_number: $line_number}})
                        SET n += $props
                        MERGE (f)-[:CONTAINS]->(n)
                    """
                    session.run(query, file_path=file_path_str, name=item['name'], line_number=item['line_number'], props=item)
                    
                    if label == 'Function':
                        for arg_name in item.get('args', []):
                            session.run("""
                                MATCH (fn:Function {name: $func_name, file_path: $file_path, line_number: $line_number})
                                MERGE (p:Parameter {name: $arg_name, file_path: $file_path, function_line_number: $line_number})
                                MERGE (fn)-[:HAS_PARAMETER]->(p)
                            """, func_name=item['name'], file_path=file_path_str, line_number=item['line_number'], arg_name=arg_name)

            # Create CONTAINS relationships for nested functions
            for item in file_data.get('functions', []):
                if item.get("context_type") == "function_definition":
                    session.run("""
                        MATCH (outer:Function {name: $context, file_path: $file_path})
                        MATCH (inner:Function {name: $name, file_path: $file_path, line_number: $line_number})
                        MERGE (outer)-[:CONTAINS]->(inner)
                    """, context=item["context"], file_path=file_path_str, name=item["name"], line_number=item["line_number"])

            # Handle imports and create IMPORTS relationships
            for imp in file_data.get('imports', []):
                info_logger(f"Processing import: {imp}")
                lang = file_data.get('lang')
                if lang == 'javascript':
                    # New, correct logic for JS
                    module_name = imp.get('source')
                    if not module_name: continue

                    # Use a map for relationship properties to handle optional alias
                    rel_props = {'imported_name': imp.get('name', '*')}
                    if imp.get('alias'):
                        rel_props['alias'] = imp.get('alias')

                    session.run("""
                        MATCH (f:File {path: $file_path})
                        MERGE (m:Module {name: $module_name})
                        MERGE (f)-[r:IMPORTS]->(m)
                        SET r += $props
                    """, file_path=file_path_str, module_name=module_name, props=rel_props)
                else:
                    # Existing logic for Python (and other languages)
                    set_clauses = ["m.alias = $alias"]
                    if 'full_import_name' in imp:
                        set_clauses.append("m.full_import_name = $full_import_name")
                    set_clause_str = ", ".join(set_clauses)

                    session.run(f"""
                        MATCH (f:File {{path: $file_path}})
                        MERGE (m:Module {{name: $name}})
                        SET {set_clause_str}
                        MERGE (f)-[:IMPORTS]->(m)
                    """, file_path=file_path_str, **imp)

            # Handle CONTAINS relationship between class to their children like variables
            for func in file_data.get('functions', []):
                if func.get('class_context'):
                    session.run("""
                        MATCH (c:Class {name: $class_name, file_path: $file_path})
                        MATCH (fn:Function {name: $func_name, file_path: $file_path, line_number: $func_line})
                        MERGE (c)-[:CONTAINS]->(fn)
                    """, 
                    class_name=func['class_context'],
                    file_path=file_path_str,
                    func_name=func['name'],
                    func_line=func['line_number'])

            # Class inheritance is handled in a separate pass after all files are processed.
            # Function calls are also handled in a separate pass after all files are processed.

    # Second pass to create relationships that depend on all files being present like call functions and class inheritance
    def _create_function_calls(self, session, file_data: Dict, imports_map: dict):
        """Create CALLS relationships with a unified, prioritized logic flow for all call types."""
        caller_file_path = str(Path(file_data['file_path']).resolve())
        local_function_names = {func['name'] for func in file_data.get('functions', [])}
        local_imports = {imp.get('alias') or imp['name'].split('.')[-1]: imp['name'] 
                        for imp in file_data.get('imports', [])}
        
        for call in file_data.get('function_calls', []):
            called_name = call['name']
            if called_name in __builtins__: continue

            resolved_path = None
            
            if call.get('inferred_obj_type'):
                obj_type = call['inferred_obj_type']
                possible_paths = imports_map.get(obj_type, [])
                if len(possible_paths) > 0:
                    resolved_path = possible_paths[0]
            
            else:
                lookup_name = call['full_name'].split('.')[0] if '.' in call['full_name'] else called_name
                possible_paths = imports_map.get(lookup_name, [])

                if lookup_name in local_function_names:
                    resolved_path = caller_file_path
                elif len(possible_paths) == 1:
                    resolved_path = possible_paths[0]
                elif len(possible_paths) > 1 and lookup_name in local_imports:
                    full_import_name = local_imports[lookup_name]
                    for path in possible_paths:
                        if full_import_name.replace('.', '/') in path:
                            resolved_path = path
                            break
            
            if not resolved_path:
                if called_name in imports_map and imports_map[called_name]:
                    resolved_path = imports_map[called_name][0]
                else:
                    resolved_path = caller_file_path

            caller_context = call.get('context')
            if caller_context and len(caller_context) == 3 and caller_context[0] is not None:
                caller_name, _, caller_line_number = caller_context
                session.run("""
                    MATCH (caller:Function {name: $caller_name, file_path: $caller_file_path, line_number: $caller_line_number})
                    MATCH (called:Function {name: $called_name, file_path: $called_file_path})
                    MERGE (caller)-[:CALLS {line_number: $line_number, args: $args, full_call_name: $full_call_name}]->(called)
                """,
                caller_name=caller_name,
                caller_file_path=caller_file_path,
                caller_line_number=caller_line_number,
                called_name=called_name,
                called_file_path=resolved_path,
                line_number=call['line_number'],
                args=call.get('args', []),
                full_call_name=call.get('full_name', called_name))
            else:
                session.run("""
                    MATCH (caller:File {path: $caller_file_path})
                    MATCH (called:Function {name: $called_name, file_path: $called_file_path})
                    MERGE (caller)-[:CALLS {line_number: $line_number, args: $args, full_call_name: $full_call_name}]->(called)
                """,
                caller_file_path=caller_file_path,
                called_name=called_name,
                called_file_path=resolved_path,
                line_number=call['line_number'],
                args=call.get('args', []),
                full_call_name=call.get('full_name', called_name))

    def _create_all_function_calls(self, all_file_data: list[Dict], imports_map: dict):
        """Create CALLS relationships for all functions after all files have been processed."""
        with self.driver.session() as session:
            for file_data in all_file_data:
                self._create_function_calls(session, file_data, imports_map)

    def _create_inheritance_links(self, session, file_data: Dict, imports_map: dict):
        """Create INHERITS relationships with a more robust resolution logic."""
        caller_file_path = str(Path(file_data['file_path']).resolve())
        local_class_names = {c['name'] for c in file_data.get('classes', [])}
        # Create a map of local import aliases/names to full import names
        local_imports = {imp.get('alias') or imp['name'].split('.')[-1]: imp['name']
                         for imp in file_data.get('imports', [])}

        for class_item in file_data.get('classes', []):
            if not class_item.get('bases'):
                continue

            for base_class_str in class_item['bases']:
                if base_class_str == 'object':
                    continue

                resolved_path = None
                target_class_name = base_class_str.split('.')[-1]

                # Handle qualified names like module.Class or alias.Class
                if '.' in base_class_str:
                    lookup_name = base_class_str.split('.')[0]
                    
                    # Case 1: The prefix is a known import
                    if lookup_name in local_imports:
                        full_import_name = local_imports[lookup_name]
                        possible_paths = imports_map.get(target_class_name, [])
                        # Find the path that corresponds to the imported module
                        for path in possible_paths:
                            if full_import_name.replace('.', '/') in path:
                                resolved_path = path
                                break
                # Handle simple names
                else:
                    lookup_name = base_class_str
                    # Case 2: The base class is in the same file
                    if lookup_name in local_class_names:
                        resolved_path = caller_file_path
                    # Case 3: The base class was imported directly (e.g., from module import Parent)
                    elif lookup_name in local_imports:
                        full_import_name = local_imports[lookup_name]
                        possible_paths = imports_map.get(target_class_name, [])
                        for path in possible_paths:
                            if full_import_name.replace('.', '/') in path:
                                resolved_path = path
                                break
                    # Case 4: Fallback to global map (less reliable)
                    elif lookup_name in imports_map:
                        possible_paths = imports_map[lookup_name]
                        if len(possible_paths) == 1:
                            resolved_path = possible_paths[0]
                
                # If a path was found, create the relationship
                if resolved_path:
                    session.run("""
                        MATCH (child:Class {name: $child_name, file_path: $file_path})
                        MATCH (parent:Class {name: $parent_name, file_path: $resolved_parent_file_path})
                        MERGE (child)-[:INHERITS]->(parent)
                    """,
                    child_name=class_item['name'],
                    file_path=caller_file_path,
                    parent_name=target_class_name,
                    resolved_parent_file_path=resolved_path)

    def _create_all_inheritance_links(self, all_file_data: list[Dict], imports_map: dict):
        """Create INHERITS relationships for all classes after all files have been processed."""
        with self.driver.session() as session:
            for file_data in all_file_data:
                self._create_inheritance_links(session, file_data, imports_map)
                
    def delete_file_from_graph(self, file_path: str):
        """Deletes a file and all its contained elements and relationships."""
        file_path_str = str(Path(file_path).resolve())
        with self.driver.session() as session:
            parents_res = session.run("""
                MATCH (f:File {path: $path})<-[:CONTAINS*]-(d:Directory)
                RETURN d.path as path ORDER BY d.path DESC
            """, path=file_path_str)
            parent_paths = [record["path"] for record in parents_res]

            session.run(
                """
                MATCH (f:File {path: $path})
                OPTIONAL MATCH (f)-[:CONTAINS]->(element)
                DETACH DELETE f, element
                """,
                path=file_path_str,
            )
            info_logger(f"Deleted file and its elements from graph: {file_path_str}")

            for path in parent_paths:
                session.run("""
                    MATCH (d:Directory {path: $path})
                    WHERE NOT (d)-[:CONTAINS]->()
                    DETACH DELETE d
                """, path=path)

    def delete_repository_from_graph(self, repo_path: str):
        """Deletes a repository and all its contents from the graph."""
        repo_path_str = str(Path(repo_path).resolve())
        with self.driver.session() as session:
            session.run("""MATCH (r:Repository {path: $path})
                          OPTIONAL MATCH (r)-[:CONTAINS*]->(e)
                          DETACH DELETE r, e""", path=repo_path_str)
            info_logger(f"Deleted repository and its contents from graph: {repo_path_str}")

    def update_file_in_graph(self, file_path: Path, repo_path: Path, imports_map: dict):
        """Updates a single file's nodes in the graph."""
        file_path_str = str(file_path.resolve())
        repo_name = repo_path.name
        
        self.delete_file_from_graph(file_path_str)

        if file_path.exists():
            file_data = self.parse_file(repo_path, file_path)
            
            if "error" not in file_data:
                self.add_file_to_graph(file_data, repo_name, imports_map)
                return file_data
            else:
                error_logger(f"Skipping graph add for {file_path_str} due to parsing error: {file_data['error']}")
                return None
        else:
            return {"deleted": True, "path": file_path_str}

    def parse_file(self, repo_path: Path, file_path: Path, is_dependency: bool = False) -> Dict:
        """Parses a file with the appropriate language parser and extracts code elements."""
        parser = self.parsers.get(file_path.suffix)
        if not parser:
            warning_logger(f"No parser found for file extension {file_path.suffix}. Skipping {file_path}")
            return {"file_path": str(file_path), "error": f"No parser for {file_path.suffix}"}

        debug_log(f"[parse_file] Starting parsing for: {file_path} with {parser.language_name} parser")
        try:
            if parser.language_name == 'python':
                is_notebook = file_path.suffix == '.ipynb'
                file_data = parser.parse(file_path, is_dependency, is_notebook=is_notebook)
            else:
                file_data = parser.parse(file_path, is_dependency)
            file_data['repo_path'] = str(repo_path)
            debug_log(f"[parse_file] Successfully parsed: {file_path}")
            return file_data
            
        except Exception as e:
            error_logger(f"Error parsing {file_path} with {parser.language_name} parser: {e}")
            debug_log(f"[parse_file] Error parsing {file_path}: {e}")
            return {"file_path": str(file_path), "error": str(e)}

    def estimate_processing_time(self, path: Path) -> Optional[Tuple[int, float]]:
        """Estimate processing time and file count"""
        try:
            supported_extensions = self.parsers.keys()
            if path.is_file():
                if path.suffix in supported_extensions:
                    files = [path]
                else:
                    return 0, 0.0 # Not a supported file type
            else:
                all_files = path.rglob("*")
                files = [f for f in all_files if f.is_file() and f.suffix in supported_extensions]
            
            total_files = len(files)
            estimated_time = total_files * 0.05 # tree-sitter is faster
            return total_files, estimated_time
        except Exception as e:
            error_logger(f"Could not estimate processing time for {path}: {e}")
            return None

    async def build_graph_from_path_async(
        self, path: Path, is_dependency: bool = False, job_id: str = None
    ):
        """Builds graph from a directory or file path."""
        try:
            if job_id:
                self.job_manager.update_job(job_id, status=JobStatus.RUNNING)
            
            self.add_repository_to_graph(path, is_dependency)
            repo_name = path.name

            cgcignore_path = path / ".cgcignore"
            if cgcignore_path.exists():
                with open(cgcignore_path) as f:
                    ignore_patterns = f.read().splitlines()
                spec = pathspec.PathSpec.from_lines('gitwildmatch', ignore_patterns)
            else:
                spec = None

            supported_extensions = self.parsers.keys()
            all_files = path.rglob("*") if path.is_dir() else [path]
            files = [f for f in all_files if f.is_file() and f.suffix in supported_extensions]
            if spec:
                files = [f for f in files if not spec.match_file(str(f.relative_to(path)))]
            if job_id:
                self.job_manager.update_job(job_id, total_files=len(files))
            
            debug_log("Starting pre-scan to build imports map...")
            imports_map = self._pre_scan_for_imports(files)
            debug_log(f"Pre-scan complete. Found {len(imports_map)} definitions.")

            all_file_data = []

            processed_count = 0
            for file in files:
                if file.is_file():
                    if job_id:
                        self.job_manager.update_job(job_id, current_file=str(file))
                    repo_path = path.resolve() if path.is_dir() else file.parent.resolve()
                    file_data = self.parse_file(repo_path, file, is_dependency)
                    if "error" not in file_data:
                        self.add_file_to_graph(file_data, repo_name, imports_map)
                        all_file_data.append(file_data)
                    processed_count += 1
                    if job_id:
                        self.job_manager.update_job(job_id, processed_files=processed_count)
                    await asyncio.sleep(0.01)

            self._create_all_inheritance_links(all_file_data, imports_map)
            self._create_all_function_calls(all_file_data, imports_map)
            
            if job_id:
                self.job_manager.update_job(job_id, status=JobStatus.COMPLETED, end_time=datetime.now())
        except Exception as e:
            error_message=str(e)
            error_logger(f"Failed to build graph for path {path}: {error_message}")
            if job_id:
                '''checking if the repo got deleted '''
                if "no such file found" in error_message or "deleted" in error_message or "not found" in error_message:
                    status=JobStatus.CANCELLED
                    
                else:
                    status=JobStatus.FAILED

                self.job_manager.update_job(
                    job_id, status=status, end_time=datetime.now(), errors=[str(e)]
                )

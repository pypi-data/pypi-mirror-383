"""AST parser module for parsing Python source files."""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParseError:
    """Represents an error encountered during parsing."""
    file_path: Path
    error_type: str
    message: str
    line_number: Optional[int] = None


@dataclass
class ParsedFile:
    """Represents a successfully parsed Python file."""
    file_path: Path
    ast_root: ast.Module
    imports: List[Union[ast.Import, ast.ImportFrom]] = field(default_factory=list)
    encoding: str = "utf-8"


class ASTParser:
    """Parses Python files into ASTs and caches them."""
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root
        self._cache: Dict[Path, ParsedFile] = {}
        self.parse_errors: List[ParseError] = []
        self.parsed_files: Dict[Path, ParsedFile] = {}
    
    def parse_file(self, file_path: Path) -> Optional[ParsedFile]:
        """
        Parse a single Python file into an AST.
        Args:
            file_path: Path to the Python file to parse
            
        Returns:
            ParsedFile object if successful, None if parsing failed
        """
        logger.debug(f"Parsing file: {file_path}")
        
        try:
            # Read the file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the source code into an AST
            ast_root = ast.parse(source_code, filename=str(file_path))
            # Extract imports
            imports = self._extract_imports(ast_root)
            
            # Create ParsedFile object
            parsed_file = ParsedFile(
                file_path=file_path,
                ast_root=ast_root,
                imports=imports,
                encoding='utf-8'
            )
            
            # Cache the parsed file
            self.parsed_files[file_path] = parsed_file
            
            return parsed_file
            
        except SyntaxError as e:
            error = ParseError(file_path=file_path, error_type="SyntaxError", message=str(e), line_number=e.lineno)
            self.parse_errors.append(error)
            logger.debug(f"Syntax error in {file_path}:{e.lineno} - {e.msg}")
            return None
        except UnicodeDecodeError as e:
            error = ParseError(file_path=file_path, error_type="UnicodeDecodeError", message=f"Failed to decode file: {e}")
            self.parse_errors.append(error)
            logger.debug(f"Encoding error in {file_path}: {e}")
            return None
        except Exception as e:
            error = ParseError(file_path=file_path, error_type=type(e).__name__, message=str(e))
            self.parse_errors.append(error)
            logger.debug(f"Unexpected error parsing {file_path}: {e}", exc_info=True)
            return None
    
    def parse_files(self, file_paths: List[Path]) -> Dict[Path, ParsedFile]:
        """
        Parse multiple Python files.
        
        Args:
            file_paths: List of paths to Python files
            
        Returns:
            Dictionary mapping file paths to ParsedFile objects (only successful parses)
        """
        logger.info(f"Parsing {len(file_paths)} files")
        
        for file_path in file_paths:
            self.parse_file(file_path)
        
        success_count = len(self.parsed_files)
        error_count = len(self.parse_errors)
        
        logger.info(f"Parsing complete: {success_count} successful, {error_count} errors")
        
        return self.parsed_files
    
    def _extract_imports(self, ast_root: ast.Module) -> List[Union[ast.Import, ast.ImportFrom]]:
        """
        Extract all import statements from an AST.
        
        Args:
            ast_root: Root AST node
            
        Returns:
            List of Import and ImportFrom nodes
        """
        imports: List[Union[ast.Import, ast.ImportFrom]] = []
        
        for node in ast.walk(ast_root):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.append(node)
        
        return imports
    
    def get_import_map(self, file_path: Path) -> Dict[str, str]:
        """
        Build a map of imported names to their module sources for a file.
        
        Args:
            file_path: Path to the parsed file
            
        Returns:
            Dictionary mapping imported names to module names
        """
        if file_path not in self.parsed_files:
            return {}
        
        parsed_file = self.parsed_files[file_path]
        import_map: Dict[str, str] = {}
        
        for import_node in parsed_file.imports:
            if isinstance(import_node, ast.Import):
                # Handle: import module
                # Handle: import module as alias
                for alias in import_node.names:
                    name = alias.asname if alias.asname else alias.name
                    import_map[name] = alias.name
                    
            elif isinstance(import_node, ast.ImportFrom):
                # Handle: from module import name
                # Handle: from module import name as alias
                module = import_node.module or ""
                for alias in import_node.names:
                    name = alias.asname if alias.asname else alias.name
                    import_map[name] = f"{module}.{alias.name}" if module else alias.name
        
        return import_map
    
    def clear_cache(self):
        """Clear all cached parsed files and errors."""
        self.parsed_files.clear()
        self.parse_errors.clear()
        logger.debug("Parser cache cleared")

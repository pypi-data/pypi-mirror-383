"""Base AST visitor classes for code analysis."""

import ast
import logging
from typing import Any, Dict, List, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseVisitor(ast.NodeVisitor):
    """
    Base visitor class for AST traversal.
    
    This class extends ast.NodeVisitor to provide common functionality
    for all analysis visitors in Vera Syntaxis.
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize the base visitor.
        
        Args:
            file_path: Path to the file being visited
        """
        self.file_path = file_path
        self.current_class: Optional[str] = None
        self.current_function: Optional[str] = None
        self.scope_stack: List[str] = []
    
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        """
        Visit a class definition.
        
        Args:
            node: ClassDef AST node
        """
        previous_class = self.current_class
        self.current_class = node.name
        self.scope_stack.append(f"class:{node.name}")
        
        logger.debug(f"Entering class: {node.name} at {self.file_path}:{node.lineno}")
        
        # Visit child nodes
        self.generic_visit(node)
        
        # Restore previous state
        self.scope_stack.pop()
        self.current_class = previous_class
        
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        """
        Visit a function definition.
        
        Args:
            node: FunctionDef AST node
        """
        previous_function = self.current_function
        self.current_function = node.name
        self.scope_stack.append(f"function:{node.name}")
        
        logger.debug(f"Entering function: {node.name} at {self.file_path}:{node.lineno}")
        
        # Visit child nodes
        self.generic_visit(node)
        
        # Restore previous state
        self.scope_stack.pop()
        self.current_function = previous_function
        
        return node
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> Any:
        """
        Visit an async function definition.
        
        Args:
            node: AsyncFunctionDef AST node
        """
        previous_function = self.current_function
        self.current_function = node.name
        self.scope_stack.append(f"async_function:{node.name}")
        
        logger.debug(f"Entering async function: {node.name} at {self.file_path}:{node.lineno}")
        
        # Visit child nodes
        self.generic_visit(node)
        
        # Restore previous state
        self.scope_stack.pop()
        self.current_function = previous_function
        
        return node
    
    def get_current_scope(self) -> str:
        """
        Get the current scope as a raw string.
        
        Returns:
            String representation of current scope (e.g., "class:MyClass.function:my_method")
        """
        return ".".join(self.scope_stack) if self.scope_stack else "<module>"

    def get_current_qualified_name(self) -> str:
        """
        Get the symbol-table-compatible qualified name for the current scope.
        
        Returns:
            A qualified name like 'MyClass.my_method'.
        """
        parts = []
        for scope in self.scope_stack:
            # Strip prefix like 'class:' or 'function:'
            parts.append(scope.split(':', 1)[-1])
        return ".".join(parts)
    
    def get_qualified_name(self, node: ast.AST) -> str:
        """
        Get the fully qualified name of a node.
        
        Args:
            node: AST node
            
        Returns:
            Qualified name string
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value_name = self.get_qualified_name(node.value)
            return f"{value_name}.{node.attr}"
        else:
            return "<unknown>"


class MultiPassVisitor:
    """
    Coordinator for multi-pass AST analysis.
    
    Some analyses require multiple passes over the AST to handle
    dependencies and forward references.
    """
    
    def __init__(self):
        """Initialize the multi-pass visitor."""
        self.passes: List[Tuple[BaseVisitor, Optional[str]]] = []
        self.results: Dict[str, Any] = {}
    
    def add_pass(self, visitor: BaseVisitor, name: Optional[str] = None) -> None:
        """
        Add a visitor pass to the analysis.
        
        Args:
            visitor: Visitor to add
            name: Optional name for the pass (defaults to class name + index)
        """
        self.passes.append((visitor, name))
    
    def run_passes(self, ast_root: ast.Module) -> Dict[str, Any]:
        """
        Run all registered passes on an AST.
        
        Args:
            ast_root: Root AST node
            
        Returns:
            Dictionary of results from all passes
        """
        logger.info(f"Running {len(self.passes)} analysis passes")
        
        for i, (visitor, custom_name) in enumerate(self.passes, 1):
            # Generate unique key for this pass
            if custom_name:
                key = custom_name
            else:
                key = f"{type(visitor).__name__}_{i}"
            
            logger.debug(f"Running pass {i}/{len(self.passes)}: {key}")
            visitor.visit(ast_root)
            self.results[key] = visitor
        
        return self.results

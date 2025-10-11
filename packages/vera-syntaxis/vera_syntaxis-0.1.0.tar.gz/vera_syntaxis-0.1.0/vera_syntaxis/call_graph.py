"""Call graph construction module."""

import ast
import logging
import networkx as nx  # type: ignore
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from vera_syntaxis.parser import ASTParser
from vera_syntaxis.visitor import BaseVisitor
from vera_syntaxis.symbol_table import SymbolTable, MethodSymbol, ClassSymbol, VariableSymbol, Symbol

logger = logging.getLogger(__name__)

class CallGraphBuilder(BaseVisitor):
    """AST visitor that builds a call graph from the codebase."""

    def __init__(self, file_path: Path, parser: ASTParser, symbol_table: SymbolTable, call_graph: nx.DiGraph):
        super().__init__(file_path)
        self.parser = parser
        self.symbol_table = symbol_table
        self.call_graph = call_graph
        self._current_symbol: Optional[Symbol] = None
        # Determine module path for qualified names
        try:
            # This is a simplified way to get the module path
            self.module_path = file_path.relative_to(self.parser.project_root).with_suffix('').as_posix().replace('/', '.')
            if self.module_path.endswith('.__init__'):
                self.module_path = self.module_path.rsplit('.__init__', 1)[0]
        except (ValueError, AttributeError):
            self.module_path = file_path.stem

    def visit_Call(self, node: ast.Call):
        """Visit a function call and add an edge to the call graph."""
        # Get the caller (the function we are currently inside)
        # Get the qualified name of the current function/method
        if not self._current_symbol:
            self.generic_visit(node)
            return
        caller_q_name = self._current_symbol.qualified_name
        caller_symbol = self.symbol_table.get_symbol(caller_q_name)

        if not isinstance(caller_symbol, MethodSymbol):
            self.generic_visit(node)
            return

        # Resolve the callee
        callee_q_name = self._resolve_callee_q_name(node.func, caller_symbol)
        if not callee_q_name:
            self.generic_visit(node)
            return

        callee_symbol = self.symbol_table.get_symbol(callee_q_name)
        if not isinstance(callee_symbol, MethodSymbol):
            self.generic_visit(node)
            return

        # Add edge to the graph
        logger.debug(f"Adding call graph edge: {caller_q_name} -> {callee_q_name}")
        self.call_graph.add_edge(caller_q_name, callee_q_name)

    def visit_ClassDef(self, node: ast.ClassDef):
        q_name = f"{self.module_path}.{node.name}"
        previous_symbol = self._current_symbol
        self._current_symbol = self.symbol_table.get_symbol(q_name)
        self.generic_visit(node)
        self._current_symbol = previous_symbol

    def visit_FunctionDef(self, node: ast.FunctionDef):
        if self._current_symbol:
            parent_prefix = f"{self._current_symbol.qualified_name}."
        else:
            parent_prefix = f"{self.module_path}."
        q_name = f"{parent_prefix}{node.name}"

        previous_symbol = self._current_symbol
        self._current_symbol = self.symbol_table.get_symbol(q_name)
        self.generic_visit(node)
        self._current_symbol = previous_symbol

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def _resolve_callee_q_name(self, node: ast.expr, caller_symbol: MethodSymbol) -> Optional[str]:
        """Attempt to resolve the qualified name of a callee."""
        if isinstance(node, ast.Name):
            if node.id == 'self':
                return 'self'  # Special case for self keyword

            # Direct function call, e.g., my_func()
            # Check imports to find the qualified name
            import_map = self.parser.get_import_map(self.file_path)
            q_name = import_map.get(node.id)
            if q_name and self.symbol_table.get_symbol(q_name):
                return q_name
            # Assume it's in the same module
            module_path = self.file_path.stem # Simplified
            return f"{module_path}.{node.id}"

        elif isinstance(node, ast.Attribute):
            # Method call, e.g., obj.my_method()
            value_node = node.value
            base_q_name = self._resolve_callee_q_name(value_node, caller_symbol)
            if not base_q_name:
                return None

            # The base_q_name could be a variable or a class name
            base_symbol = self.symbol_table.get_symbol(base_q_name)

            if isinstance(base_symbol, VariableSymbol) and base_symbol.type_hint:
                # The variable has a type hint, use that as the base for the method call
                # e.g., self.service_a has type hint 'ServiceA'
                # We need to find the qualified name for 'ServiceA'
                type_hint_symbol = self.symbol_table.get_symbol(f"{self.file_path.stem}.{base_symbol.type_hint}") # Simplified
                if type_hint_symbol:
                    return f"{type_hint_symbol.qualified_name}.{node.attr}"
                else: # Fallback for imported types
                    return f"{base_symbol.type_hint}.{node.attr}"

            elif isinstance(base_symbol, ClassSymbol):
                # Direct call on a class (e.g. MyClass.static_method())
                return f"{base_symbol.qualified_name}.{node.attr}"

            # Fallback for self.method()
            if base_q_name == 'self' and caller_symbol.parent:
                return f"{caller_symbol.parent.qualified_name}.{node.attr}"

        return None

def build_call_graph(parser: ASTParser, symbol_table: SymbolTable, parsed_files: Dict[Path, Any]) -> nx.DiGraph:
    """Build a call graph from the symbol table and parsed files."""
    graph = nx.DiGraph()
    for file_path, parsed_file in parsed_files.items():
        builder = CallGraphBuilder(file_path, parser, symbol_table, graph)
        builder.visit(parsed_file.ast_root)
    return graph

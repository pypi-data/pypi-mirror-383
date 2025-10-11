"""Symbol table for representing the codebase's structure."""

import ast
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Union

from vera_syntaxis.visitor import BaseVisitor

logger = logging.getLogger(__name__)

@dataclass
class Symbol:
    """Base class for all symbols."""
    name: str
    file_path: Path
    line_number: int
    parent: Optional['Symbol'] = None

    @property
    def qualified_name(self) -> str:
        """Generate the fully qualified name for the symbol."""
        # This will now be set directly during creation
        return self.name

@dataclass
class VariableSymbol(Symbol):
    """Represents a variable symbol."""
    type_hint: Optional[str] = None

@dataclass
class MethodSymbol(Symbol):
    """Represents a function or method symbol."""
    args: List[str] = field(default_factory=list)
    arg_types: Dict[str, str] = field(default_factory=dict)
    return_type: Optional[str] = None
    is_async: bool = False

@dataclass
class ClassSymbol(Symbol):
    """Represents a class symbol."""
    base_classes: List[str] = field(default_factory=list)
    methods: Dict[str, MethodSymbol] = field(default_factory=dict)
    attributes: Dict[str, VariableSymbol] = field(default_factory=dict)

class SymbolTable:
    """Container for all symbols in the codebase."""
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}

    def add_symbol(self, symbol: Symbol):
        """Add a symbol to the table."""
        q_name = symbol.qualified_name
        if q_name in self.symbols:
            logger.warning(f"Duplicate symbol found: {q_name}. Overwriting.")
        self.symbols[q_name] = symbol
        logger.debug(f"Added symbol: {q_name}")

    def get_symbol(self, qualified_name: str) -> Optional[Symbol]:
        """Retrieve a symbol by its qualified name."""
        return self.symbols.get(qualified_name)

    def __len__(self) -> int:
        return len(self.symbols)

class SymbolTableBuilder(BaseVisitor):
    """AST visitor that builds a symbol table from the codebase."""

    def __init__(self, file_path: Path, project_root: Path, symbol_table: SymbolTable):
        super().__init__(file_path)
        self.symbol_table = symbol_table
        self._current_symbol: Optional[Symbol] = None
        # Determine module path for qualified names
        try:
            self.module_path = file_path.relative_to(project_root).with_suffix('').as_posix().replace('/', '.')
            if self.module_path.endswith('.__init__'):
                self.module_path = self.module_path.rsplit('.__init__', 1)[0]
        except ValueError:
            self.module_path = file_path.stem

    def _node_to_string(self, node: Optional[ast.AST]) -> Optional[str]:
        """Convert an AST node to its string representation."""
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        # Fallback for complex annotations
        return ast.unparse(node).strip()

    def visit_ClassDef(self, node: ast.ClassDef):
        q_name = f"{self.module_path}.{node.name}"
        class_symbol = ClassSymbol(
            name=q_name,
            file_path=self.file_path,
            line_number=node.lineno,
            base_classes=[self._node_to_string(b) for b in node.bases if self._node_to_string(b)],
            parent=self._current_symbol
        )
        self.symbol_table.add_symbol(class_symbol)

        # Process children with the class as the current symbol
        previous_symbol = self._current_symbol
        self._current_symbol = class_symbol
        self.generic_visit(node)
        self._current_symbol = previous_symbol

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._process_function(node, is_async=False)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._process_function(node, is_async=True)

    def _process_function(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef], is_async: bool):
        # Exclude 'self', 'cls', 'ctx' from arguments
        special_args = {'self', 'cls', 'ctx'}
        args = [arg.arg for arg in node.args.args if arg.arg not in special_args]
        arg_types = {arg.arg: self._node_to_string(arg.annotation) for arg in node.args.args if arg.annotation and arg.arg not in special_args}
        return_type = self._node_to_string(node.returns)

        parent_prefix = f"{self._current_symbol.qualified_name}." if self._current_symbol else f"{self.module_path}."
        q_name = f"{parent_prefix}{node.name}"

        method_symbol = MethodSymbol(
            name=q_name,
            file_path=self.file_path,
            line_number=node.lineno,
            args=args,
            arg_types=arg_types,
            return_type=return_type,
            is_async=is_async,
            parent=self._current_symbol
        )
        self.symbol_table.add_symbol(method_symbol)

        # Add to parent class if inside one
        if isinstance(self._current_symbol, ClassSymbol):
            self._current_symbol.methods[node.name] = method_symbol

        # Process children
        previous_symbol = self._current_symbol
        self._current_symbol = method_symbol
        self.generic_visit(node)
        self._current_symbol = previous_symbol

    def visit_AnnAssign(self, node: ast.AnnAssign):
        # Only capture class or module-level annotated assignments
        if isinstance(self._current_symbol, (ClassSymbol, type(None))):
            if isinstance(node.target, ast.Name):
                var_name = node.target.id
                type_hint = self._node_to_string(node.annotation)

                if isinstance(self._current_symbol, ClassSymbol):
                    # Class attribute
                    q_name = f"{self._current_symbol.qualified_name}.{var_name}"
                    parent_symbol = self._current_symbol
                else:
                    # Module-level variable
                    q_name = f"{self.module_path}.{var_name}"
                    parent_symbol = None

                var_symbol = VariableSymbol(
                    name=q_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    type_hint=type_hint,
                    parent=parent_symbol
                )
                self.symbol_table.add_symbol(var_symbol)

                if isinstance(parent_symbol, ClassSymbol):
                    parent_symbol.attributes[var_name] = var_symbol
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        # Try to infer type from the right-hand side of the assignment
        inferred_type = None
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
            inferred_type = node.value.func.id
        elif isinstance(node.value, ast.Name):
            # Assignment from another variable, e.g., self.x = y
            # Check if 'y' is an argument of the current method with a known type
            if isinstance(self._current_symbol, MethodSymbol):
                inferred_type = self._current_symbol.arg_types.get(node.value.id)

        for target in node.targets:
            var_symbol = None
            attr_key = None
            parent_for_attr = None

            # Case 1: Instance attribute assignment (e.g., self.x = ...)
            if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                if isinstance(self._current_symbol, MethodSymbol) and self._current_symbol.parent:
                    class_symbol = self._current_symbol.parent
                    attr_name = target.attr
                    q_name = f"{class_symbol.qualified_name}.{attr_name}"
                    var_symbol = VariableSymbol(
                        name=q_name,
                        file_path=self.file_path,
                        line_number=node.lineno,
                        type_hint=inferred_type,
                        parent=class_symbol
                    )
                    attr_key = attr_name
                    parent_for_attr = class_symbol

            # Case 2: Class or module level assignment (e.g., MY_VAR = ...)
            elif isinstance(target, ast.Name):
                var_name = target.id
                if isinstance(self._current_symbol, ClassSymbol):
                    q_name = f"{self._current_symbol.qualified_name}.{var_name}"
                    parent_symbol = self._current_symbol
                    attr_key = var_name
                    parent_for_attr = self._current_symbol
                elif self._current_symbol is None:
                    q_name = f"{self.module_path}.{var_name}"
                    parent_symbol = None
                else: # Inside a function, ignore for now
                    continue
                
                var_symbol = VariableSymbol(
                    name=q_name,
                    file_path=self.file_path,
                    line_number=node.lineno,
                    type_hint=inferred_type,
                    parent=parent_symbol
                )

            if var_symbol:
                self.symbol_table.add_symbol(var_symbol)
                if attr_key and isinstance(parent_for_attr, ClassSymbol):
                    parent_for_attr.attributes[attr_key] = var_symbol

        self.generic_visit(node)

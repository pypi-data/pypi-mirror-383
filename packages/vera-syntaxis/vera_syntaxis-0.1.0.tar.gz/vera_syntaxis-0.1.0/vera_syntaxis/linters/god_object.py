"""Linter for detecting God Objects (classes with too many responsibilities)."""

import ast
import logging
from pathlib import Path
from typing import List

from vera_syntaxis.linter_base import BaseLinter, register_linter
from vera_syntaxis.violations import Violation
from vera_syntaxis.symbol_table import ClassSymbol

logger = logging.getLogger(__name__)


@register_linter("god_object")
class GodObjectLinter(BaseLinter):
    """Detects God Objects - classes with too many responsibilities."""

    @property
    def rule_id(self) -> str:
        return "GO001"

    def run(self) -> None:
        """Run the god object detection."""
        logger.info("Running God Object linter...")

        config = self.context.config.god_object

        logger.debug(f"Symbol table has {len(self.context.symbol_table.symbols)} symbols")

        # Analyze each class in the symbol table
        for symbol_name, symbol in self.context.symbol_table.symbols.items():
            if not isinstance(symbol, ClassSymbol):
                continue
            
            logger.debug(f"Analyzing class: {symbol.name}")

            # Count methods and attributes
            method_count = self._count_methods(symbol)
            attribute_count = self._count_attributes(symbol)
            line_count = self._count_lines(symbol)

            logger.debug(f"Class {symbol.name}: {method_count} methods, {attribute_count} attributes, {line_count} lines")

            violations = []

            # Check method count
            if method_count > config.max_methods:
                violations.append(f"{method_count} methods (max: {config.max_methods})")

            # Check attribute count
            if attribute_count > config.max_attributes:
                violations.append(f"{attribute_count} attributes (max: {config.max_attributes})")

            # Check line count
            if line_count > config.max_lines:
                violations.append(f"{line_count} lines (max: {config.max_lines})")

            # Create violation if any threshold exceeded
            if violations:
                violation_details = ", ".join(violations)
                message = (f"God Object detected: Class '{symbol.name}' has too many responsibilities - "
                           f"{violation_details}. Consider splitting into smaller, focused classes.")

                violation = Violation(
                    rule_id=self.rule_id,
                    message=message,
                    file_path=symbol.file_path,
                    line_number=symbol.line_number
                )
                self.add_violation(violation)

        logger.info(f"God Object linter finished, found {len(self.violations)} violations.")

    def _count_methods(self, class_symbol: ClassSymbol) -> int:
        """Count the number of methods in a class."""
        if not class_symbol.file_path or class_symbol.file_path not in self.context.parsed_files:
            return 0

        parsed_file = self.context.parsed_files[class_symbol.file_path]
        
        # Find the class node in the AST
        class_node = self._find_class_node(parsed_file.ast_root, class_symbol.name)
        if not class_node:
            return 0

        # Count function definitions (methods)
        method_count = 0
        for node in ast.walk(class_node):
            if isinstance(node, ast.FunctionDef):
                # Only count direct children (not nested functions)
                if self._is_direct_child(class_node, node):
                    method_count += 1

        return method_count

    def _count_attributes(self, class_symbol: ClassSymbol) -> int:
        """Count the number of attributes in a class."""
        if not class_symbol.file_path or class_symbol.file_path not in self.context.parsed_files:
            return 0

        parsed_file = self.context.parsed_files[class_symbol.file_path]
        
        # Find the class node in the AST
        class_node = self._find_class_node(parsed_file.ast_root, class_symbol.name)
        if not class_node:
            return 0

        # Count attributes (assignments in __init__ and class-level)
        attributes = set()

        # Class-level attributes
        for node in class_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        attributes.add(target.id)

        # Instance attributes in __init__
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                for child in ast.walk(node):
                    if isinstance(child, ast.Assign):
                        for target in child.targets:
                            if isinstance(target, ast.Attribute):
                                if isinstance(target.value, ast.Name) and target.value.id == 'self':
                                    attributes.add(target.attr)

        return len(attributes)

    def _count_lines(self, class_symbol: ClassSymbol) -> int:
        """Count the number of lines in a class."""
        if not class_symbol.file_path or class_symbol.file_path not in self.context.parsed_files:
            return 0

        parsed_file = self.context.parsed_files[class_symbol.file_path]
        
        # Find the class node in the AST
        class_node = self._find_class_node(parsed_file.ast_root, class_symbol.name)
        if not class_node:
            return 0

        # Calculate line count
        if hasattr(class_node, 'end_lineno') and class_node.end_lineno:
            return class_node.end_lineno - class_node.lineno + 1

        return 0

    def _find_class_node(self, tree: ast.AST, class_name: str) -> ast.ClassDef:
        """Find a class node by name in the AST."""
        # Extract just the class name (last part after dots)
        simple_name = class_name.split('.')[-1]
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == simple_name:
                return node
        return None

    def _is_direct_child(self, class_node: ast.ClassDef, func_node: ast.FunctionDef) -> bool:
        """Check if a function is a direct child of a class (not nested)."""
        return func_node in class_node.body

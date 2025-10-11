"""Linter for detecting Feature Envy (methods that belong in another class)."""

import ast
import logging
from pathlib import Path
from typing import Dict, Set
from collections import defaultdict

from vera_syntaxis.linter_base import BaseLinter, register_linter
from vera_syntaxis.violations import Violation
from vera_syntaxis.symbol_table import ClassSymbol

logger = logging.getLogger(__name__)


@register_linter("feature_envy")
class FeatureEnvyLinter(BaseLinter):
    """Detects Feature Envy - methods that use more features from another class than their own."""

    @property
    def rule_id(self) -> str:
        return "FE001"

    def run(self) -> None:
        """Run the feature envy detection."""
        logger.info("Running Feature Envy linter...")

        config = self.context.config.feature_envy

        # Analyze each class in the symbol table
        for symbol_name, symbol in self.context.symbol_table.symbols.items():
            if not isinstance(symbol, ClassSymbol):
                continue

            logger.debug(f"Analyzing class: {symbol.name}")

            # Analyze each method in the class
            methods = self._get_methods(symbol)
            logger.debug(f"Class {symbol.name} has {len(methods)} methods: {list(methods.keys())}")
            for method_name, method_node in methods.items():
                self._analyze_method(symbol, method_name, method_node, config)

        logger.info(f"Feature Envy linter finished, found {len(self.violations)} violations.")

    def _get_methods(self, class_symbol: ClassSymbol) -> Dict[str, ast.FunctionDef]:
        """Get all methods in a class."""
        methods = {}

        if not class_symbol.file_path or class_symbol.file_path not in self.context.parsed_files:
            return methods

        parsed_file = self.context.parsed_files[class_symbol.file_path]
        class_node = self._find_class_node(parsed_file.ast_root, class_symbol.name)

        if not class_node:
            return methods

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                methods[node.name] = node

        return methods

    def _analyze_method(self, class_symbol: ClassSymbol, method_name: str, 
                       method_node: ast.FunctionDef, config) -> None:
        """Analyze a method for feature envy."""
        logger.debug(f"Analyzing method: {method_name}")
        
        # Skip __init__ and other magic methods
        if method_name.startswith('__') and method_name.endswith('__'):
            logger.debug(f"Skipping magic method: {method_name}")
            return

        # Count accesses
        self_accesses = 0  # Access to self
        external_accesses = defaultdict(int)  # Accesses to other objects

        for node in ast.walk(method_node):
            if isinstance(node, ast.Attribute):
                # Get the root object being accessed (e.g., for self.account.balance, get 'self' and 'account')
                root, first_attr = self._get_attribute_root(node)
                
                if root == 'self' and first_attr:
                    # This is accessing a member of self (e.g., self.account.balance)
                    # Count this as an external access to 'account'
                    external_accesses[first_attr] += 1
                elif root == 'self':
                    # Direct self access (e.g., self.balance)
                    self_accesses += 1
                elif root:
                    # Direct external access (e.g., account.balance where account is a parameter)
                    external_accesses[root] += 1

        # Find the most-accessed external object
        if not external_accesses:
            return

        max_external_obj = max(external_accesses, key=external_accesses.get)
        max_external_count = external_accesses[max_external_obj]

        total_accesses = self_accesses + sum(external_accesses.values())

        logger.debug(f"Method {method_name}: self={self_accesses}, external={dict(external_accesses)}, total={total_accesses}")

        # Check if method has enough accesses to be meaningful
        if total_accesses < config.min_accesses:
            logger.debug(f"Method {method_name}: skipped (total_accesses {total_accesses} < min {config.min_accesses})")
            return

        # Check if external accesses exceed threshold
        external_ratio = max_external_count / total_accesses if total_accesses > 0 else 0

        logger.debug(f"Method {method_name}: external_ratio={external_ratio:.2f}, threshold={config.envy_threshold}")

        if external_ratio > config.envy_threshold:
            message = (f"Feature Envy detected: Method '{method_name}' in class '{class_symbol.name.split('.')[-1]}' "
                       f"accesses '{max_external_obj}' {max_external_count} times but 'self' only {self_accesses} times "
                       f"({external_ratio:.1%} external access). Consider moving this method to the '{max_external_obj}' class.")

            violation = Violation(
                rule_id=self.rule_id,
                message=message,
                file_path=class_symbol.file_path,
                line_number=method_node.lineno
            )
            self.add_violation(violation)

    def _get_attribute_root(self, node: ast.Attribute) -> tuple:
        """
        Get the root object and first attribute from an attribute chain.
        
        For self.account.balance, returns ('self', 'account')
        For self.balance, returns ('self', None)
        For account.balance, returns ('account', None)
        """
        # Walk up the attribute chain to find the root
        current = node
        attrs = []
        
        while isinstance(current, ast.Attribute):
            attrs.append(current.attr)
            current = current.value
        
        # current should now be a Name node (the root object)
        if isinstance(current, ast.Name):
            root = current.id
            # attrs is reversed (innermost to outermost), so reverse it
            attrs.reverse()
            first_attr = attrs[0] if attrs else None
            return (root, first_attr)
        
        return (None, None)

    def _find_class_node(self, tree: ast.AST, class_name: str) -> ast.ClassDef:
        """Find a class node by name in the AST."""
        # Extract just the class name (last part after dots)
        simple_name = class_name.split('.')[-1]

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == simple_name:
                return node
        return None

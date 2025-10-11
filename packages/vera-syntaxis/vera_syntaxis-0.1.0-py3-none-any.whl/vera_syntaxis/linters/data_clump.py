"""Linter for detecting Data Clumps (groups of parameters that always appear together)."""

import ast
import logging
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from itertools import combinations

from vera_syntaxis.linter_base import BaseLinter, register_linter
from vera_syntaxis.violations import Violation
from vera_syntaxis.symbol_table import ClassSymbol

logger = logging.getLogger(__name__)


@register_linter("data_clump")
class DataClumpLinter(BaseLinter):
    """Detects Data Clumps - groups of parameters that frequently appear together."""

    @property
    def rule_id(self) -> str:
        return "DC001"

    def run(self) -> None:
        """Run the data clump detection."""
        logger.info("Running Data Clump linter...")

        config = self.context.config.data_clump

        # Analyze each class in the symbol table
        for symbol_name, symbol in self.context.symbol_table.symbols.items():
            if not isinstance(symbol, ClassSymbol):
                continue

            logger.debug(f"Analyzing class: {symbol.name}")

            # Get all methods and their parameters
            methods_params = self._get_methods_with_params(symbol)
            
            if len(methods_params) < config.min_occurrences:
                logger.debug(f"Skipping class {symbol.name}: only {len(methods_params)} methods")
                continue

            # Find parameter clumps
            clumps = self._find_parameter_clumps(methods_params, config)

            # Report violations
            for clump_params, method_names in clumps.items():
                if len(method_names) >= config.min_occurrences:
                    self._create_clump_violation(symbol, clump_params, method_names)

        logger.info(f"Data Clump linter finished, found {len(self.violations)} violations.")

    def _get_methods_with_params(self, class_symbol: ClassSymbol) -> Dict[str, List[str]]:
        """Get all methods in a class with their parameter names."""
        methods_params = {}

        if not class_symbol.file_path or class_symbol.file_path not in self.context.parsed_files:
            return methods_params

        parsed_file = self.context.parsed_files[class_symbol.file_path]
        class_node = self._find_class_node(parsed_file.ast_root, class_symbol.name)

        if not class_node:
            return methods_params

        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Skip magic methods
                if node.name.startswith('__') and node.name.endswith('__'):
                    continue

                # Extract parameter names (exclude 'self')
                params = []
                for arg in node.args.args:
                    if arg.arg != 'self':
                        params.append(arg.arg)

                if params:  # Only include methods with parameters
                    methods_params[node.name] = params

        return methods_params

    def _find_parameter_clumps(self, methods_params: Dict[str, List[str]], config) -> Dict[Tuple[str, ...], List[str]]:
        """Find groups of parameters that appear together in multiple methods."""
        # Track which methods contain which parameter groups
        clump_methods = defaultdict(list)

        # For each method, generate all possible parameter combinations
        for method_name, params in methods_params.items():
            # Generate combinations of size >= min_clump_size
            for size in range(config.min_clump_size, len(params) + 1):
                for combo in combinations(sorted(params), size):
                    clump_methods[combo].append(method_name)

        # Filter to only keep clumps that appear in multiple methods
        filtered_clumps = {}
        for clump, methods in clump_methods.items():
            if len(methods) >= config.min_occurrences:
                # Check if this is not a subset of a larger clump with the same methods
                is_maximal = True
                for other_clump, other_methods in clump_methods.items():
                    if (len(other_clump) > len(clump) and 
                        set(clump).issubset(set(other_clump)) and 
                        set(methods) == set(other_methods)):
                        is_maximal = False
                        break
                
                if is_maximal:
                    filtered_clumps[clump] = methods

        return filtered_clumps

    def _create_clump_violation(self, class_symbol: ClassSymbol, clump_params: Tuple[str, ...], method_names: List[str]):
        """Create a violation for a data clump."""
        params_str = ", ".join(clump_params)
        methods_str = ", ".join(method_names)
        
        message = (f"Data Clump detected: Parameters ({params_str}) appear together in {len(method_names)} methods "
                   f"({methods_str}) in class '{class_symbol.name.split('.')[-1]}'. "
                   f"Consider extracting these parameters into a dedicated class.")

        violation = Violation(
            rule_id=self.rule_id,
            message=message,
            file_path=class_symbol.file_path,
            line_number=class_symbol.line_number
        )
        self.add_violation(violation)

    def _find_class_node(self, tree: ast.AST, class_name: str) -> ast.ClassDef:
        """Find a class node by name in the AST."""
        # Extract just the class name (last part after dots)
        simple_name = class_name.split('.')[-1]

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == simple_name:
                return node
        return None

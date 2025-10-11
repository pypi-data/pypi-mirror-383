"""Linter for detecting various forms of tight coupling."""

import ast
import logging
from pathlib import Path
from typing import List, Dict, Set
from collections import defaultdict

from vera_syntaxis.linter_base import BaseLinter, LinterContext, register_linter
from vera_syntaxis.violations import Violation
from vera_syntaxis.symbol_table import ClassSymbol
from vera_syntaxis.visitor import BaseVisitor

logger = logging.getLogger(__name__)


class DirectInstantiationVisitor(BaseVisitor):
    """An AST visitor that finds direct instantiations of other classes."""
    def __init__(self, linter: 'TightCouplingLinter', file_path: Path):
        super().__init__(file_path=file_path)
        self.linter = linter
        self.violations: List[Violation] = []

    def visit_Call(self, node: ast.Call):
        # We are looking for a call that instantiates a class, e.g., MyClass()
        if isinstance(node.func, ast.Name):
            callee_name = node.func.id
            
            # Resolve the name using the file's import map
            parser = self.linter.context.parser
            import_map = parser.get_import_map(self.file_path)
            
            # Resolve the callee's qualified name
            qualified_callee_name = import_map.get(callee_name)
            if not qualified_callee_name:
                # If not in imports, assume it's in the same module.
                try:
                    module_path = self.file_path.relative_to(self.linter.context.parser.project_root).with_suffix('').as_posix().replace('/', '.')
                    if module_path.endswith('.__init__'):
                        module_path = module_path.rsplit('.__init__', 1)[0]
                except (ValueError, AttributeError):
                    module_path = self.file_path.stem
                qualified_callee_name = f"{module_path}.{callee_name}"

            callee_symbol = self.linter.context.symbol_table.get_symbol(qualified_callee_name)

            if isinstance(callee_symbol, ClassSymbol):
                # We are inside a method, and we are instantiating another class.
                # This is a direct instantiation.
                # Get the qualified name of the current class from the visitor's scope stack
                try:
                    module_path = self.file_path.relative_to(self.linter.context.parser.project_root).with_suffix('').as_posix().replace('/', '.')
                    if module_path.endswith('.__init__'):
                        module_path = module_path.rsplit('.__init__', 1)[0]
                except (ValueError, AttributeError):
                    module_path = self.file_path.stem
                current_class_q_name = f"{module_path}.{self.current_class}"
                
                if current_class_q_name != callee_symbol.qualified_name:
                    violation = Violation(
                        rule_id=self.linter.rule_id,
                        message=f"Direct instantiation of class '{callee_name}' inside method '{self.current_function}' of class '{self.current_class}'. Consider using dependency injection.",
                        file_path=self.file_path,
                        line_number=node.lineno,
                        column_number=node.col_offset
                    )
                    self.violations.append(violation)

        self.generic_visit(node)


class LawOfDemeterVisitor(BaseVisitor):
    """An AST visitor that detects violations of the Law of Demeter (excessive method chaining)."""

    def __init__(self, linter: 'TightCouplingLinter', file_path: Path):
        super().__init__(file_path=file_path)
        self.linter = linter
        self.violations: List[Violation] = []
        self.max_chain_length = linter.context.config.coupling.max_demeter_chain

    def visit_Expr(self, node: ast.Expr):
        """Visit expression statements to check for method chains."""
        if isinstance(node.value, (ast.Attribute, ast.Call)):
            chain_length = self._count_chain_length(node.value)
            if chain_length > self.max_chain_length:
                violation = Violation(
                    rule_id="TC002",
                    message=(f"Law of Demeter violation: Method chain length ({chain_length}) "
                             f"exceeds maximum ({self.max_chain_length}). "
                             f"Consider breaking the chain or using intermediate variables."),
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_number=node.col_offset
                )
                self.violations.append(violation)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """Visit assignment statements to check for method chains in the value."""
        chain_length = self._count_chain_length(node.value)
        if chain_length > self.max_chain_length:
            violation = Violation(
                rule_id="TC002",
                message=(f"Law of Demeter violation: Method chain length ({chain_length}) "
                         f"exceeds maximum ({self.max_chain_length}). "
                         f"Consider breaking the chain or using intermediate variables."),
                file_path=self.file_path,
                line_number=node.lineno,
                column_number=node.col_offset
            )
            self.violations.append(violation)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return):
        """Visit return statements to check for method chains in the return value."""
        if node.value:
            chain_length = self._count_chain_length(node.value)
            if chain_length > self.max_chain_length:
                violation = Violation(
                    rule_id="TC002",
                    message=(f"Law of Demeter violation: Method chain length ({chain_length}) "
                             f"exceeds maximum ({self.max_chain_length}). "
                             f"Consider breaking the chain or using intermediate variables."),
                    file_path=self.file_path,
                    line_number=node.lineno,
                    column_number=node.col_offset
                )
                self.violations.append(violation)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        """Visit function calls to check for method chains in arguments."""
        # Check each argument for method chains
        for arg in node.args:
            chain_length = self._count_chain_length(arg)
            if chain_length > self.max_chain_length:
                violation = Violation(
                    rule_id="TC002",
                    message=(f"Law of Demeter violation: Method chain length ({chain_length}) "
                             f"exceeds maximum ({self.max_chain_length}). "
                             f"Consider breaking the chain or using intermediate variables."),
                    file_path=self.file_path,
                    line_number=arg.lineno if hasattr(arg, 'lineno') else node.lineno,
                    column_number=arg.col_offset if hasattr(arg, 'col_offset') else node.col_offset
                )
                self.violations.append(violation)
        self.generic_visit(node)

    def _count_chain_length(self, node: ast.AST) -> int:
        """
        Count the length of an attribute/method call chain.

        Examples:
        - obj.method() -> 1
        - obj.attr.method() -> 2
        - obj.get_a().get_b().get_c() -> 3
        """
        count = 0
        current = node

        while True:
            if isinstance(current, ast.Attribute):
                count += 1
                current = current.value
            elif isinstance(current, ast.Call):
                # Count the call itself and continue with the function being called
                if isinstance(current.func, ast.Attribute):
                    count += 1
                    current = current.func.value
                else:
                    # It's a simple function call, not a method chain
                    break
            else:
                # Reached the base (e.g., a Name node like 'obj')
                break

        return count


class ExcessiveInteractionChecker:
    """Analyzes the call graph to detect classes with excessive inter-class interactions."""

    def __init__(self, linter: 'TightCouplingLinter'):
        self.linter = linter
        self.violations: List[Violation] = []
        self.max_calls = linter.context.config.coupling.max_inter_class_calls

    def check_interactions(self) -> None:
        """
        Analyze the call graph to find classes with too many inter-class calls.
        
        For each class, count how many unique methods from OTHER classes it calls.
        """
        call_graph = self.linter.context.call_graph
        symbol_table = self.linter.context.symbol_table

        # Build a map of class -> set of external methods called
        class_interactions: Dict[str, Set[str]] = defaultdict(set)

        # Iterate through all edges in the call graph
        for caller, callee in call_graph.edges():
            # Extract class names from qualified method names
            # Format: "module.ClassName.method_name"
            caller_class = self._extract_class_name(caller)
            callee_class = self._extract_class_name(callee)

            # Only count if both are valid classes and they're different
            if caller_class and callee_class and caller_class != callee_class:
                class_interactions[caller_class].add(callee)

        # Check each class for excessive interactions
        for class_name, called_methods in class_interactions.items():
            interaction_count = len(called_methods)
            if interaction_count > self.max_calls:
                # Find the class symbol to get file location
                class_symbol = symbol_table.get_symbol(class_name)
                if isinstance(class_symbol, ClassSymbol):
                    # Count unique target classes
                    target_classes = set()
                    for method in called_methods:
                        target_class = self._extract_class_name(method)
                        if target_class:
                            target_classes.add(target_class)

                    violation = Violation(
                        rule_id="TC003",
                        message=(f"Excessive interaction: Class '{class_name.split('.')[-1]}' "
                                 f"calls {interaction_count} methods from {len(target_classes)} "
                                 f"other class(es), exceeding maximum of {self.max_calls}. "
                                 f"Consider refactoring to reduce coupling."),
                        file_path=class_symbol.file_path,
                        line_number=class_symbol.line_number
                    )
                    self.violations.append(violation)

    def _extract_class_name(self, qualified_name: str) -> str:
        """
        Extract the class name from a qualified method name.
        
        Examples:
        - "module.ClassName.method_name" -> "module.ClassName"
        - "ClassName.method_name" -> "ClassName"
        - "function_name" -> ""
        """
        parts = qualified_name.split('.')
        if len(parts) >= 2:
            # Return everything except the last part (method name)
            return '.'.join(parts[:-1])
        return ""


@register_linter("tight_coupling")
class TightCouplingLinter(BaseLinter):
    """Checks for various forms of tight coupling between classes."""

    def __init__(self, context: LinterContext):
        super().__init__(context)
        self.current_file = None

    @property
    def rule_id(self) -> str:
        return "TC001"

    def run(self) -> None:
        """Run the tight coupling checks across all relevant files."""
        logger.info("Running Tight Coupling linter...")

        for file_path, parsed_file in self.context.parsed_files.items():
            # Check for direct instantiation (TC001)
            instantiation_visitor = DirectInstantiationVisitor(self, file_path)
            instantiation_visitor.visit(parsed_file.ast_root)
            self.violations.extend(instantiation_visitor.violations)

            # Check for Law of Demeter violations (TC002)
            demeter_visitor = LawOfDemeterVisitor(self, file_path)
            demeter_visitor.visit(parsed_file.ast_root)
            self.violations.extend(demeter_visitor.violations)

        # Check for excessive interaction using call graph (TC003)
        interaction_checker = ExcessiveInteractionChecker(self)
        interaction_checker.check_interactions()
        self.violations.extend(interaction_checker.violations)

        logger.info(f"Tight Coupling linter finished, found {len(self.violations)} violations.")

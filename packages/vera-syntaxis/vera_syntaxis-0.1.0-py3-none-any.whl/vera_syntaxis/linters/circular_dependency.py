"""Linter for detecting circular dependencies between modules and classes."""

import logging
from pathlib import Path
from typing import List, Set, Tuple, Dict
import networkx as nx  # type: ignore

from vera_syntaxis.linter_base import BaseLinter, register_linter
from vera_syntaxis.violations import Violation

logger = logging.getLogger(__name__)


@register_linter("circular_dependency")
class CircularDependencyLinter(BaseLinter):
    """Detects circular dependencies between modules and classes."""

    @property
    def rule_id(self) -> str:
        return "CD001"

    def run(self) -> None:
        """Run the circular dependency detection."""
        logger.info("Running Circular Dependency linter...")

        config = self.context.config.circular

        # Build a dependency graph at the module/class level
        # This is more reliable than using the call graph which requires actual method calls
        dependency_graph = self._build_dependency_graph()

        logger.debug(f"Dependency graph has {dependency_graph.number_of_nodes()} nodes and {dependency_graph.number_of_edges()} edges")

        # Find all simple cycles in the dependency graph
        try:
            cycles = list(nx.simple_cycles(dependency_graph))
            logger.debug(f"Found {len(cycles)} cycles")
        except Exception as e:
            logger.error(f"Error detecting cycles: {e}")
            return

        # Filter and report cycles
        reported_cycles: Set[Tuple[str, ...]] = set()

        for cycle in cycles:
            # Skip self-cycles if configured
            if len(cycle) == 1 and config.allow_self_cycles:
                continue

            # Skip cycles that are too long
            if len(cycle) > config.max_cycle_length:
                logger.debug(f"Skipping cycle of length {len(cycle)} (exceeds max_cycle_length)")
                continue

            # Normalize cycle to avoid reporting the same cycle multiple times
            # (e.g., [A, B, C] and [B, C, A] are the same cycle)
            normalized_cycle = self._normalize_cycle(cycle)

            if normalized_cycle in reported_cycles:
                continue

            reported_cycles.add(normalized_cycle)

            # Create violation
            violation = self._create_cycle_violation(cycle)
            if violation:
                self.add_violation(violation)

        logger.info(f"Circular Dependency linter finished, found {len(self.violations)} cycles.")

    def _build_dependency_graph(self) -> nx.DiGraph:
        """Build a dependency graph from imports and symbol usage."""
        graph = nx.DiGraph()

        # For each file, add edges based on what it imports and uses
        for file_path, parsed_file in self.context.parsed_files.items():
            # Get the module name for this file
            source_module = self._get_module_name(file_path)

            # Get all imports for this file
            import_map = self.context.parser.get_import_map(file_path)

            # Add edges for each import
            for imported_name, qualified_name in import_map.items():
                # Find the symbol to get its module
                symbol = self.context.symbol_table.get_symbol(qualified_name)
                if symbol and symbol.file_path and symbol.file_path != file_path:
                    target_module = self._get_module_name(symbol.file_path)
                    if source_module and target_module and source_module != target_module:
                        graph.add_edge(source_module, target_module)
                        logger.debug(f"Added edge: {source_module} -> {target_module}")

        return graph

    def _get_module_name(self, file_path: Path) -> str:
        """Get a module name from a file path."""
        try:
            project_root = self.context.parser.project_root
            if project_root:
                relative_path = file_path.relative_to(project_root)
                # Convert path to module name (e.g., "foo/bar.py" -> "foo.bar")
                module_name = str(relative_path.with_suffix('')).replace('\\', '.').replace('/', '.')
                # Remove __init__ from the end if present
                if module_name.endswith('.__init__'):
                    module_name = module_name[:-9]
                return module_name
        except ValueError:
            pass

        # Fallback to just the stem
        return file_path.stem

    def _normalize_cycle(self, cycle: List[str]) -> Tuple[str, ...]:
        """
        Normalize a cycle to a canonical form.
        
        This ensures that [A, B, C], [B, C, A], and [C, A, B] are all
        represented the same way.
        """
        if not cycle:
            return tuple()

        # Find the lexicographically smallest element
        min_idx = cycle.index(min(cycle))

        # Rotate the cycle to start with the smallest element
        normalized = cycle[min_idx:] + cycle[:min_idx]

        return tuple(normalized)

    def _create_cycle_violation(self, cycle: List[str]) -> Violation:
        """Create a violation for a detected cycle."""
        if not cycle:
            return None

        # Extract module/class information from the first node in the cycle
        first_node = cycle[0]
        file_path, line_number = self._get_location_for_node(first_node)

        if not file_path:
            return None

        # Create a readable cycle description
        cycle_description = " → ".join(self._shorten_name(node) for node in cycle)
        cycle_description += f" → {self._shorten_name(cycle[0])}"  # Complete the cycle

        if len(cycle) == 1:
            message = (f"Self-referential cycle detected: {self._shorten_name(cycle[0])} calls itself. "
                       f"Consider refactoring to avoid recursion or enable 'allow_self_cycles' if intentional.")
        else:
            message = (f"Circular dependency detected involving {len(cycle)} components: {cycle_description}. "
                       f"Consider introducing an interface or breaking the cycle with dependency inversion.")

        return Violation(
            rule_id=self.rule_id,
            message=message,
            file_path=file_path,
            line_number=line_number
        )

    def _get_location_for_node(self, node: str) -> Tuple[Path, int]:
        """Get the file path and line number for a node in the call graph."""
        # Try to find the symbol in the symbol table
        symbol = self.context.symbol_table.get_symbol(node)

        if symbol and symbol.file_path:
            return symbol.file_path, symbol.line_number

        # If not found, try to infer from the node name
        # Node format is typically "module.Class.method"
        parts = node.split('.')
        if len(parts) >= 2:
            # Try to find the class
            class_name = '.'.join(parts[:-1])
            class_symbol = self.context.symbol_table.get_symbol(class_name)
            if class_symbol and class_symbol.file_path:
                return class_symbol.file_path, class_symbol.line_number

        # Fallback: try to find any file that might contain this
        for file_path in self.context.parsed_files.keys():
            # Simple heuristic: if the node name contains part of the file name
            if parts[0] in str(file_path):
                return file_path, 1

        return None, 1

    def _shorten_name(self, qualified_name: str) -> str:
        """Shorten a qualified name for display."""
        parts = qualified_name.split('.')
        if len(parts) <= 2:
            return qualified_name

        # Return Class.method or just the last two parts
        return '.'.join(parts[-2:])

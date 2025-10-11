"""Linter for enforcing Model-View-Business-Controller (MVBC) architecture."""

import ast
import logging
from pathlib import Path
from typing import Dict

from vera_syntaxis.linter_base import BaseLinter, register_linter
from vera_syntaxis.violations import Violation

logger = logging.getLogger(__name__)


@register_linter("mvbc")
class MVBCLinter(BaseLinter):
    """Ensures that dependencies flow in the correct direction in an MVBC architecture."""

    @property
    def rule_id(self) -> str:
        return "W2902"

    def run(self) -> None:
        """Run the linter to find illegal cross-layer imports."""
        if not self.context.config.mvbc:
            logger.debug("MVBC linter is not configured. Skipping.")
            return

        layer_map = self._map_files_to_layers()

        for source_path, parsed_file in self.context.parsed_files.items():
            source_layer = layer_map.get(source_path)
            if not source_layer:
                continue

            import_map = self.context.parser.get_import_map(source_path)
            for imported_name, qualified_name in import_map.items():
                target_symbol = self.context.symbol_table.get_symbol(qualified_name)
                if not target_symbol or not target_symbol.file_path:
                    continue

                target_layer = layer_map.get(target_symbol.file_path)
                if not target_layer:
                    continue

                if not self._is_allowed_dependency(source_layer, target_layer):
                    suggestion = self._get_suggestion(source_layer, target_layer)
                    msg = (f"Illegal MVBC dependency: Layer '{source_layer}' cannot import "
                           f"from layer '{target_layer}' ('{imported_name}'). "
                           f"{suggestion}")
                    violation = Violation(
                        rule_id=self.rule_id,
                        message=msg,
                        file_path=source_path,
                        line_number=self._find_import_line(
                            parsed_file.ast_root, imported_name, qualified_name
                        )
                    )
                    self.add_violation(violation)

    def _map_files_to_layers(self) -> Dict[Path, str]:
        """Create a mapping from file paths to their architectural layer."""
        layer_map: Dict[Path, str] = {}
        mvbc_config = self.context.config.mvbc
        project_root = self.context.parser.project_root

        if not mvbc_config or not project_root:
            return layer_map

        layer_patterns = {
            "Model": mvbc_config.model_paths,
            "View": mvbc_config.view_paths,
            "Business": mvbc_config.business_paths,
            "Controller": mvbc_config.controller_paths,
        }

        all_files = self.context.parsed_files.keys()

        for layer, patterns in layer_patterns.items():
            for pattern in patterns:
                for file_path in all_files:
                    try:
                        relative_path = file_path.relative_to(project_root)
                        # Support both single-level and nested patterns
                        # e.g., "models/*.py" and "models/**/*.py"
                        if file_path not in layer_map and self._matches_pattern(relative_path, pattern):
                            layer_map[file_path] = layer
                    except ValueError:
                        # File is not relative to project root, skip it
                        pass

        return layer_map

    def _matches_pattern(self, path: Path, pattern: str) -> bool:
        """Check if a path matches a glob pattern, supporting both single and nested directories."""
        # Try direct match first
        if path.match(pattern):
            return True
        
        # If pattern contains **, it already handles nested directories
        if "**" in pattern:
            return False
        
        # If pattern doesn't have **, also try with ** inserted
        # e.g., "models/*.py" should also match "models/subdir/file.py"
        # Convert "models/*.py" to "models/**/*.py"
        parts = pattern.split('/')
        if len(parts) >= 2:
            nested_pattern = '/'.join(parts[:-1]) + '/**/' + parts[-1]
            if path.match(nested_pattern):
                return True
        
        return False

    def _is_allowed_dependency(self, source_layer: str, target_layer: str) -> bool:
        """
        Check if a dependency between two layers is allowed in MVBC architecture.
        
        Allowed dependencies:
        - Model: Can be used by anyone (no dependencies on other layers)
        - View: Can use Model only
        - Business: Can use Model only
        - Controller: Can use View, Business, and Model
        
        Forbidden dependencies:
        - View → Business (must go through Controller)
        - Business → View (business logic shouldn't know about presentation)
        - View → Controller (creates circular dependency)
        - Business → Controller (creates circular dependency)
        """
        # Imports within the same layer are allowed
        if source_layer == target_layer:
            return True

        # Model can be used by anyone
        if target_layer == "Model":
            return True

        # Controller can use View and Business
        if source_layer == "Controller" and target_layer in ["View", "Business"]:
            return True

        # View can only use Model (already handled above)
        # Business can only use Model (already handled above)
        # Everything else is forbidden
        return False

    def _get_suggestion(self, source_layer: str, target_layer: str) -> str:
        """Get a helpful suggestion for fixing the layer violation."""
        if source_layer == "View" and target_layer == "Business":
            return "Views should not directly access Business logic. Use a Controller to mediate."
        elif source_layer == "Business" and target_layer == "View":
            return "Business logic should not depend on Views. Keep business logic independent of presentation."
        elif source_layer == "View" and target_layer == "Controller":
            return "Views should not import Controllers. Controllers should instantiate and manage Views."
        elif source_layer == "Business" and target_layer == "Controller":
            return "Business logic should not depend on Controllers. Controllers should orchestrate Business logic."
        else:
            return "Consider refactoring to follow MVBC layer dependencies: Controller → View/Business → Model."

    def _find_import_line(self, ast_root, imported_name: str, qualified_name: str) -> int:
        """Find the line number of a specific import statement."""
        for node in ast.walk(ast_root):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names:
                    # Construct the qualified name for the alias as the parser does
                    if isinstance(node, ast.ImportFrom) and node.module:
                        current_q_name = f"{node.module}.{alias.name}"
                    else:
                        current_q_name = alias.name
                    current_name = alias.asname or alias.name
                    if current_name == imported_name and (
                        current_q_name == qualified_name or alias.name == qualified_name
                    ):
                        return node.lineno
        return 1

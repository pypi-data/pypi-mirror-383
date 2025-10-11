"""Factory Method pattern detector."""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Set

from vera_syntaxis.pattern_detectors.base import BasePatternDetector, PatternOpportunity
from vera_syntaxis.symbol_table import ClassSymbol

logger = logging.getLogger(__name__)


@dataclass
class InstantiationInfo:
    """Information about a class instantiation."""
    file_path: Path
    line_number: int
    class_name: str
    qualified_name: str


class FactoryDetector(BasePatternDetector):
    """Detects opportunities for Factory Method pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Factory Method"
    
    @property
    def pattern_description(self) -> str:
        return "Decouple object creation from usage when multiple related types need instantiation"
    
    def detect(self) -> List[PatternOpportunity]:
        """
        Detect Factory Method pattern opportunities.
        
        Looks for:
        1. Multiple direct instantiations of related classes
        2. Class families scattered across different files
        
        Returns:
            List of PatternOpportunity objects
        """
        logger.debug("Running Factory Method pattern detection")
        
        # Collect all class instantiations
        instantiations = self._collect_instantiations()
        
        if not instantiations:
            return []
        
        # Group by class families (classes with common base)
        families = self._group_by_class_family(instantiations)
        
        # Detect opportunities
        opportunities = []
        for base_class, instances in families.items():
            if len(instances) >= 3:  # Need at least 3 instantiations
                # Check if scattered across files
                unique_files = set(inst.file_path for inst in instances)
                
                if len(unique_files) >= 2:  # Scattered across 2+ files
                    confidence = self._calculate_factory_confidence(instances, unique_files)
                    opportunity = self._create_factory_opportunity(
                        base_class, instances, confidence
                    )
                    opportunities.append(opportunity)
                    logger.debug(f"Found Factory opportunity: {base_class} ({len(instances)} instances)")
        
        self.opportunities = opportunities
        return opportunities
    
    def _collect_instantiations(self) -> Dict[str, List[InstantiationInfo]]:
        """
        Collect all class instantiations from parsed files.
        
        Returns:
            Dictionary mapping qualified class names to instantiation info
        """
        instantiations = defaultdict(list)
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.Call):
                    # Check if this is a direct class call
                    class_name = self._extract_class_name(node.func)
                    
                    if class_name:
                        # Try to resolve to symbol table
                        qualified_name = self._resolve_qualified_name(class_name, file_path)
                        
                        if qualified_name:
                            symbol = self.context.symbol_table.get_symbol(qualified_name)
                            
                            # Only track if it's a class
                            if isinstance(symbol, ClassSymbol):
                                instantiations[qualified_name].append(
                                    InstantiationInfo(
                                        file_path=file_path,
                                        line_number=node.lineno,
                                        class_name=class_name,
                                        qualified_name=qualified_name
                                    )
                                )
        
        return instantiations
    
    def _extract_class_name(self, node: ast.expr) -> str:
        """Extract class name from call node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handle module.ClassName calls
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.insert(0, current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.insert(0, current.id)
            return '.'.join(parts)
        return None
    
    def _resolve_qualified_name(self, class_name: str, file_path: Path) -> str:
        """Resolve class name to qualified name using import map."""
        # Try direct lookup in symbol table
        for qualified_name, symbol in self.context.symbol_table.symbols.items():
            if isinstance(symbol, ClassSymbol):
                if qualified_name.endswith(f".{class_name}"):
                    return qualified_name
        
        # Try import map
        import_map = self.context.parser.get_import_map(file_path)
        if class_name in import_map:
            return import_map[class_name]
        
        return None
    
    def _group_by_class_family(
        self, 
        instantiations: Dict[str, List[InstantiationInfo]]
    ) -> Dict[str, List[InstantiationInfo]]:
        """
        Group instantiations by class family (classes with common base).
        
        Args:
            instantiations: Dict of qualified name to instantiation list
        
        Returns:
            Dict of base class to all instantiations of derived classes
        """
        families = defaultdict(list)
        
        for qualified_name, instances in instantiations.items():
            symbol = self.context.symbol_table.get_symbol(qualified_name)
            
            if isinstance(symbol, ClassSymbol):
                # Find base class
                if symbol.base_classes and len(symbol.base_classes) > 0:
                    # Use first base class as family identifier
                    base = symbol.base_classes[0]
                    families[base].extend(instances)
                else:
                    # No explicit base, use class itself as family
                    # (may be multiple unrelated instantiations)
                    if len(instances) >= 3:
                        families[qualified_name].extend(instances)
        
        return families
    
    def _calculate_factory_confidence(
        self, 
        instances: List[InstantiationInfo],
        unique_files: Set[Path]
    ) -> float:
        """
        Calculate confidence score for Factory pattern opportunity.
        
        Args:
            instances: List of instantiation occurrences
            unique_files: Set of files where instantiations occur
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.5  # Base confidence
        
        # More instances = higher confidence
        if len(instances) >= 5:
            confidence += 0.3
        elif len(instances) >= 4:
            confidence += 0.2
        elif len(instances) >= 3:
            confidence += 0.1
        
        # Scattered across more files = higher confidence
        if len(unique_files) >= 3:
            confidence += 0.2
        elif len(unique_files) >= 2:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _create_factory_opportunity(
        self,
        base_class: str,
        instances: List[InstantiationInfo],
        confidence: float
    ) -> PatternOpportunity:
        """Create PatternOpportunity for Factory pattern."""
        # Get unique class names
        class_names = set(inst.class_name for inst in instances)
        unique_files = set(inst.file_path for inst in instances)
        
        # Use first instance location
        first_instance = instances[0]
        
        description = (
            f"Found {len(instances)} instantiations of {len(class_names)} related classes "
            f"({', '.join(sorted(class_names))}) across {len(unique_files)} files"
        )
        
        benefit = (
            "Centralizes object creation, enables runtime type selection, "
            "simplifies adding new types, reduces coupling"
        )
        
        example_code = self._generate_example_code(base_class, class_names)
        
        return self._create_opportunity(
            file_path=first_instance.file_path,
            line_number=first_instance.line_number,
            confidence=confidence,
            description=description,
            trigger_type="Multiple Direct Instantiations",
            benefit=benefit,
            example_code=example_code,
            related_files=list(unique_files),
            evidence={
                'instance_count': len(instances),
                'class_count': len(class_names),
                'file_count': len(unique_files),
                'base_class': base_class,
                'classes': list(class_names)
            }
        )
    
    def _generate_example_code(self, base_class: str, class_names: Set[str]) -> str:
        """Generate example Factory implementation."""
        # Simplified base class name
        simple_base = base_class.split('.')[-1] if '.' in base_class else base_class
        factory_name = f"{simple_base}Factory"
        
        example = f"""# Before: Direct instantiations
# obj1 = {list(class_names)[0]}()
# obj2 = {list(class_names)[1] if len(class_names) > 1 else list(class_names)[0]}()

# After: Factory Method pattern
class {factory_name}:
    @staticmethod
    def create(type_name: str) -> {simple_base}:
        if type_name == "type1":
            return {list(class_names)[0]}()
        elif type_name == "type2":
            return {list(class_names)[1] if len(class_names) > 1 else list(class_names)[0]}()
        # Add more types as needed
        raise ValueError(f"Unknown type: {{type_name}}")

# Usage
obj = {factory_name}.create("type1")
"""
        return example

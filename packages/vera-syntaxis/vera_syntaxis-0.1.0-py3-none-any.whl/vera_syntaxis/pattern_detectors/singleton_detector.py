"""Singleton Pattern detector."""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict

from vera_syntaxis.pattern_detectors.base import BasePatternDetector, PatternOpportunity
from vera_syntaxis.symbol_table import ClassSymbol

logger = logging.getLogger(__name__)


@dataclass
class InstantiationInfo:
    """Information about class instantiation."""
    file_path: Path
    line_number: int
    class_name: str


class SingletonDetector(BasePatternDetector):
    """Detects opportunities for Singleton pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Singleton"
    
    @property
    def pattern_description(self) -> str:
        return "Ensure only one instance of a class exists globally"
    
    def detect(self) -> List[PatternOpportunity]:
        """Detect Singleton pattern opportunities."""
        logger.debug("Running Singleton pattern detection")
        
        opportunities = []
        
        # Find multiple instantiations of stateful classes
        multi_instantiations = self._find_multiple_instantiations()
        
        for class_name, instances in multi_instantiations.items():
            if len(instances) >= 2 and self._is_stateful_class(class_name):
                confidence = 0.85 if len(instances) >= 3 else 0.65
                opportunity = self._create_singleton_opportunity(
                    class_name, instances, confidence
                )
                opportunities.append(opportunity)
        
        # Find global instance patterns
        global_instances = self._find_global_instances()
        for global_info in global_instances:
            confidence = 0.9 if global_info['has_lazy_init'] else 0.7
            opportunity = self._create_formalize_singleton_opportunity(
                global_info, confidence
            )
            opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _find_multiple_instantiations(self) -> Dict[str, List[InstantiationInfo]]:
        """Find classes instantiated multiple times."""
        instantiations = defaultdict(list)
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        class_name = node.func.id
                        instantiations[class_name].append(
                            InstantiationInfo(
                                file_path=file_path,
                                line_number=node.lineno,
                                class_name=class_name
                            )
                        )
        
        return instantiations
    
    def _is_stateful_class(self, class_name: str) -> bool:
        """Check if class is stateful (has instance attributes)."""
        # Check in symbol table
        for qualified_name, symbol in self.context.symbol_table.symbols.items():
            if isinstance(symbol, ClassSymbol):
                if qualified_name.endswith(f".{class_name}"):
                    # Check for instance variables
                    return len(symbol.attributes) > 0
        return False
    
    def _find_global_instances(self) -> List[dict]:
        """Find global instance patterns."""
        patterns = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            # Look for module-level variables that hold class instances
            for node in parsed_file.ast_root.body:
                if isinstance(node, ast.Assign):
                    # Check if assigned value is None or a class instantiation
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            
                            # Check if there's a getter function
                            has_lazy_init = self._has_getter_function(
                                parsed_file.ast_root, var_name
                            )
                            
                            if has_lazy_init:
                                patterns.append({
                                    'file_path': file_path,
                                    'variable_name': var_name,
                                    'line_number': node.lineno,
                                    'has_lazy_init': True
                                })
        
        return patterns
    
    def _has_getter_function(self, module: ast.Module, var_name: str) -> bool:
        """Check if there's a getter function for the variable."""
        for node in module.body:
            if isinstance(node, ast.FunctionDef):
                # Check if function name suggests getter
                if 'get' in node.name.lower() or 'instance' in node.name.lower():
                    # Check if it references the variable
                    for stmt in ast.walk(node):
                        if isinstance(stmt, ast.Name) and stmt.id == var_name:
                            return True
        return False
    
    def _create_singleton_opportunity(
        self,
        class_name: str,
        instances: List[InstantiationInfo],
        confidence: float
    ) -> PatternOpportunity:
        """Create PatternOpportunity for Singleton."""
        unique_files = set(inst.file_path for inst in instances)
        
        description = (
            f"Class '{class_name}' instantiated {len(instances)} times "
            f"across {len(unique_files)} files. Consider Singleton if only one instance needed"
        )
        
        benefit = (
            "Ensures single instance, provides global access point, "
            "saves memory, maintains consistent state"
        )
        
        example = f"""# Before: Multiple instantiations
# obj1 = {class_name}()
# obj2 = {class_name}()

# After: Singleton pattern
class {class_name}:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# Usage
obj1 = {class_name}()
obj2 = {class_name}()
assert obj1 is obj2  # Same instance
"""
        
        return self._create_opportunity(
            file_path=instances[0].file_path,
            line_number=instances[0].line_number,
            confidence=confidence,
            description=description,
            trigger_type="Multiple Instantiations",
            benefit=benefit,
            example_code=example,
            related_files=list(unique_files),
            evidence={
                'instance_count': len(instances),
                'file_count': len(unique_files),
                'class_name': class_name
            }
        )
    
    def _create_formalize_singleton_opportunity(
        self,
        global_info: dict,
        confidence: float
    ) -> PatternOpportunity:
        """Create opportunity for formalizing global instance pattern."""
        description = (
            f"Global variable '{global_info['variable_name']}' with lazy initialization. "
            f"Formalize as Singleton pattern"
        )
        
        benefit = "Thread-safe singleton, cleaner API, testable"
        
        example = f"""# Before: Global variable
# {global_info['variable_name']} = None
# def get_instance():
#     global {global_info['variable_name']}
#     if {global_info['variable_name']} is None:
#         {global_info['variable_name']} = MyClass()
#     return {global_info['variable_name']}

# After: Proper Singleton
class MyClass:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
"""
        
        return self._create_opportunity(
            file_path=global_info['file_path'],
            line_number=global_info['line_number'],
            confidence=confidence,
            description=description,
            trigger_type="Global Instance Pattern",
            benefit=benefit,
            example_code=example,
            evidence=global_info
        )

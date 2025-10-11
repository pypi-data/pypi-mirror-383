"""Decorator Pattern detector (structural, not @decorator)."""

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
class WrapperClass:
    """Information about a wrapper class."""
    name: str
    file_path: Path
    line_number: int
    wrapped_param: str
    delegations: List[str]


class DecoratorPatternDetector(BasePatternDetector):
    """Detects opportunities for Decorator pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Decorator"
    
    @property
    def pattern_description(self) -> str:
        return "Add behavior to objects dynamically through wrapping"
    
    def detect(self) -> List[PatternOpportunity]:
        """Detect Decorator pattern opportunities."""
        logger.debug("Running Decorator pattern detection")
        
        opportunities = []
        
        # Find wrapper classes
        wrappers = self._find_wrapper_classes()
        
        # Group by wrapped type
        by_type = self._group_by_wrapped_type(wrappers)
        
        for wrapped_type, wrapper_list in by_type.items():
            if len(wrapper_list) >= 2:
                confidence = 0.95 if len(wrapper_list) >= 3 else 0.85
                opportunity = self._create_decorator_opportunity(
                    wrapped_type, wrapper_list, confidence
                )
                opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _find_wrapper_classes(self) -> List[WrapperClass]:
        """Find classes that wrap other objects."""
        wrappers = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.ClassDef):
                    # Check __init__ for wrapping pattern
                    init_method = self._find_init_method(node)
                    
                    if init_method:
                        wrapped_param = self._find_wrapped_parameter(init_method)
                        
                        if wrapped_param:
                            # Check for delegation pattern
                            delegations = self._find_delegations(node, wrapped_param)
                            
                            if len(delegations) >= 2:
                                wrappers.append(WrapperClass(
                                    name=node.name,
                                    file_path=file_path,
                                    line_number=node.lineno,
                                    wrapped_param=wrapped_param,
                                    delegations=delegations
                                ))
        
        return wrappers
    
    def _find_init_method(self, class_node: ast.ClassDef) -> ast.FunctionDef:
        """Find __init__ method in class."""
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name == '__init__':
                return node
        return None
    
    def _find_wrapped_parameter(self, init_method: ast.FunctionDef) -> str:
        """Find parameter that represents wrapped object."""
        # Look for parameters stored as instance attributes
        for stmt in init_method.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            # Check if assigned from parameter
                            if isinstance(stmt.value, ast.Name):
                                # Found: self.x = param
                                return target.attr
        return None
    
    def _find_delegations(self, class_node: ast.ClassDef, wrapped_attr: str) -> List[str]:
        """Find methods that delegate to wrapped object."""
        delegations = []
        
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and node.name != '__init__':
                # Check if method calls wrapped object's methods
                for stmt in ast.walk(node):
                    if isinstance(stmt, ast.Call):
                        if isinstance(stmt.func, ast.Attribute):
                            # Check if calling self.wrapped_attr.method()
                            if isinstance(stmt.func.value, ast.Attribute):
                                if (isinstance(stmt.func.value.value, ast.Name) and
                                    stmt.func.value.value.id == 'self' and
                                    stmt.func.value.attr == wrapped_attr):
                                    method_name = stmt.func.attr
                                    if method_name not in delegations:
                                        delegations.append(method_name)
        
        return delegations
    
    def _group_by_wrapped_type(self, wrappers: List[WrapperClass]) -> Dict[str, List[WrapperClass]]:
        """Group wrappers by what they wrap (heuristic based on naming)."""
        by_type = defaultdict(list)
        
        for wrapper in wrappers:
            # Simple heuristic: extract base name from wrapper class
            # e.g., "LoggingDatabase" -> "Database"
            base_type = self._extract_base_type(wrapper.name)
            by_type[base_type].append(wrapper)
        
        return by_type
    
    def _extract_base_type(self, wrapper_name: str) -> str:
        """Extract base type from wrapper class name."""
        # Remove common prefixes/suffixes
        prefixes = ['Logging', 'Caching', 'Retry', 'Tracing', 'Timing']
        suffixes = ['Wrapper', 'Decorator', 'Proxy']
        
        base = wrapper_name
        for prefix in prefixes:
            if base.startswith(prefix):
                base = base[len(prefix):]
                break
        
        for suffix in suffixes:
            if base.endswith(suffix):
                base = base[:-len(suffix)]
                break
        
        return base or wrapper_name
    
    def _create_decorator_opportunity(
        self,
        wrapped_type: str,
        wrappers: List[WrapperClass],
        confidence: float
    ) -> PatternOpportunity:
        """Create PatternOpportunity for Decorator pattern."""
        wrapper_names = [w.name for w in wrappers]
        
        description = (
            f"Found {len(wrappers)} wrapper classes for '{wrapped_type}': "
            f"{', '.join(wrapper_names)}. Formalize as Decorator pattern"
        )
        
        benefit = (
            "Enables dynamic behavior composition, follows Open/Closed Principle, "
            "avoids class explosion from inheritance"
        )
        
        example = f"""# Before: Multiple wrapper classes
# class LoggingDatabase:
#     def __init__(self, db):
#         self.db = db
#     def query(self, sql):
#         log(sql)
#         return self.db.query(sql)

# After: Decorator pattern
class {wrapped_type}Decorator(ABC):
    def __init__(self, component: {wrapped_type}):
        self._component = component
    
    @abstractmethod
    def operation(self):
        pass

class LoggingDecorator({wrapped_type}Decorator):
    def operation(self):
        log("Operation called")
        return self._component.operation()

# Usage - stackable decorators
db = LoggingDecorator(CachingDecorator(Database()))
"""
        
        related_files = list(set(w.file_path for w in wrappers))
        
        return self._create_opportunity(
            file_path=wrappers[0].file_path,
            line_number=wrappers[0].line_number,
            confidence=confidence,
            description=description,
            trigger_type="Multiple Wrapper Classes",
            benefit=benefit,
            example_code=example,
            related_files=related_files,
            evidence={
                'wrapper_count': len(wrappers),
                'wrappers': wrapper_names,
                'base_type': wrapped_type
            }
        )

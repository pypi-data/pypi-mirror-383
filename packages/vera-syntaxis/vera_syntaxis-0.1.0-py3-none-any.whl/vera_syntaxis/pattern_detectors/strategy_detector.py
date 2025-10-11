"""Strategy Pattern detector."""

import ast
import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from vera_syntaxis.pattern_detectors.base import BasePatternDetector, PatternOpportunity

logger = logging.getLogger(__name__)


@dataclass
class ConditionalBranch:
    """Information about a conditional branch."""
    type_checked: str
    operations: List[str]


@dataclass
class ConditionalCase:
    """Information about a conditional structure."""
    file_path: Path
    line_number: int
    function_name: str
    condition_type: str
    branches: List[ConditionalBranch]
    variable_name: str


class StrategyDetector(BasePatternDetector):
    """Detects opportunities for Strategy pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Strategy"
    
    @property
    def pattern_description(self) -> str:
        return "Replace conditional logic with polymorphic strategy objects"
    
    def detect(self) -> List[PatternOpportunity]:
        """Detect Strategy pattern opportunities."""
        logger.debug("Running Strategy pattern detection")
        
        opportunities = []
        
        # Find isinstance conditionals
        isinstance_cases = self._find_isinstance_conditionals()
        for case in isinstance_cases:
            if len(case.branches) >= 3:
                confidence = 0.9 if len(case.branches) >= 4 else 0.8
                opportunity = self._create_strategy_opportunity(case, confidence)
                opportunities.append(opportunity)
        
        # Find string/enum conditionals
        string_cases = self._find_string_conditionals()
        for case in string_cases:
            if len(case.branches) >= 3:
                confidence = 0.85 if len(case.branches) >= 4 else 0.7
                opportunity = self._create_strategy_opportunity(case, confidence)
                opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _find_isinstance_conditionals(self) -> List[ConditionalCase]:
        """Find if/elif chains with isinstance checks."""
        cases = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for stmt in node.body:
                        if isinstance(stmt, ast.If):
                            branches = self._collect_isinstance_branches(stmt)
                            if len(branches) >= 2:
                                var_name = self._extract_variable_from_isinstance(stmt.test)
                                cases.append(ConditionalCase(
                                    file_path=file_path,
                                    line_number=stmt.lineno,
                                    function_name=node.name,
                                    condition_type="isinstance",
                                    branches=branches,
                                    variable_name=var_name or "unknown"
                                ))
        
        return cases
    
    def _collect_isinstance_branches(self, if_node: ast.If) -> List[ConditionalBranch]:
        """Collect branches with isinstance checks."""
        branches = []
        current = if_node
        
        while current:
            if self._is_isinstance_check(current.test):
                type_checked = self._extract_type_from_isinstance(current.test)
                operations = [ast.unparse(stmt) for stmt in current.body[:2]]
                branches.append(ConditionalBranch(
                    type_checked=type_checked,
                    operations=operations
                ))
            
            if current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            else:
                break
        
        return branches
    
    def _is_isinstance_check(self, node: ast.expr) -> bool:
        """Check if node is isinstance() call."""
        return (isinstance(node, ast.Call) and 
                isinstance(node.func, ast.Name) and 
                node.func.id == 'isinstance')
    
    def _extract_type_from_isinstance(self, node: ast.expr) -> str:
        """Extract type name from isinstance check."""
        if isinstance(node, ast.Call) and len(node.args) >= 2:
            type_arg = node.args[1]
            if isinstance(type_arg, ast.Name):
                return type_arg.id
            elif isinstance(type_arg, ast.Attribute):
                return type_arg.attr
        return "Unknown"
    
    def _extract_variable_from_isinstance(self, node: ast.expr) -> Optional[str]:
        """Extract variable being checked."""
        if isinstance(node, ast.Call) and len(node.args) >= 1:
            var_arg = node.args[0]
            if isinstance(var_arg, ast.Name):
                return var_arg.id
        return None
    
    def _find_string_conditionals(self) -> List[ConditionalCase]:
        """Find if/elif chains with string comparisons."""
        cases = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    for stmt in node.body:
                        if isinstance(stmt, ast.If):
                            branches = self._collect_string_branches(stmt)
                            if len(branches) >= 2:
                                var_name = self._extract_variable_from_comparison(stmt.test)
                                cases.append(ConditionalCase(
                                    file_path=file_path,
                                    line_number=stmt.lineno,
                                    function_name=node.name,
                                    condition_type="string_match",
                                    branches=branches,
                                    variable_name=var_name or "unknown"
                                ))
        
        return cases
    
    def _collect_string_branches(self, if_node: ast.If) -> List[ConditionalBranch]:
        """Collect branches with string comparisons."""
        branches = []
        current = if_node
        
        while current:
            if self._is_string_comparison(current.test):
                value = self._extract_value_from_comparison(current.test)
                operations = [ast.unparse(stmt) for stmt in current.body[:2]]
                branches.append(ConditionalBranch(
                    type_checked=value,
                    operations=operations
                ))
            
            if current.orelse and len(current.orelse) == 1 and isinstance(current.orelse[0], ast.If):
                current = current.orelse[0]
            else:
                break
        
        return branches
    
    def _is_string_comparison(self, node: ast.expr) -> bool:
        """Check if node is string comparison."""
        if isinstance(node, ast.Compare):
            if isinstance(node.left, ast.Name) and len(node.comparators) > 0:
                comp = node.comparators[0]
                return isinstance(comp, ast.Constant) and isinstance(comp.value, str)
        return False
    
    def _extract_value_from_comparison(self, node: ast.expr) -> str:
        """Extract compared value."""
        if isinstance(node, ast.Compare) and len(node.comparators) > 0:
            comp = node.comparators[0]
            if isinstance(comp, ast.Constant):
                return str(comp.value)
        return "unknown"
    
    def _extract_variable_from_comparison(self, node: ast.expr) -> Optional[str]:
        """Extract variable being compared."""
        if isinstance(node, ast.Compare) and isinstance(node.left, ast.Name):
            return node.left.id
        return None
    
    def _create_strategy_opportunity(
        self, 
        case: ConditionalCase, 
        confidence: float
    ) -> PatternOpportunity:
        """Create PatternOpportunity for Strategy pattern."""
        types = [b.type_checked for b in case.branches]
        
        description = (
            f"Found {len(case.branches)} conditional branches based on "
            f"{case.condition_type} in function '{case.function_name}'"
        )
        
        benefit = (
            "Replaces conditional logic with polymorphic objects, "
            "improves extensibility, reduces cyclomatic complexity"
        )
        
        example = self._generate_example(case, types)
        
        return self._create_opportunity(
            file_path=case.file_path,
            line_number=case.line_number,
            confidence=confidence,
            description=description,
            trigger_type=f"Conditional Logic ({case.condition_type})",
            benefit=benefit,
            example_code=example,
            evidence={
                'branch_count': len(case.branches),
                'condition_type': case.condition_type,
                'function_name': case.function_name,
                'types': types
            }
        )
    
    def _generate_example(self, case: ConditionalCase, types: List[str]) -> str:
        """Generate example Strategy implementation."""
        return f"""# Before: Conditional logic
# if isinstance({case.variable_name}, {types[0]}):
#     # Handle {types[0]}
# elif isinstance({case.variable_name}, {types[1] if len(types) > 1 else types[0]}):
#     # Handle {types[1] if len(types) > 1 else types[0]}

# After: Strategy pattern
class Strategy(ABC):
    @abstractmethod
    def execute(self):
        pass

class {types[0]}Strategy(Strategy):
    def execute(self):
        # Implementation for {types[0]}
        pass

class {types[1] if len(types) > 1 else types[0]}Strategy(Strategy):
    def execute(self):
        # Implementation for {types[1] if len(types) > 1 else types[0]}
        pass

# Usage
strategy = strategy_map[type_key]
strategy.execute()
"""

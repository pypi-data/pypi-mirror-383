"""Observer Pattern detector."""

import ast
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set

from vera_syntaxis.pattern_detectors.base import BasePatternDetector, PatternOpportunity

logger = logging.getLogger(__name__)


@dataclass
class NotificationChain:
    """Information about a notification chain."""
    file_path: Path
    method_name: str
    line_number: int
    notifications: List[str]
    has_state_change: bool


class ObserverDetector(BasePatternDetector):
    """Detects opportunities for Observer pattern."""
    
    @property
    def pattern_name(self) -> str:
        return "Observer"
    
    @property
    def pattern_description(self) -> str:
        return "Decouple objects when one needs to notify many others of state changes"
    
    def detect(self) -> List[PatternOpportunity]:
        """Detect Observer pattern opportunities."""
        logger.debug("Running Observer pattern detection")
        
        opportunities = []
        
        # Find methods that notify multiple objects after state change
        notification_chains = self._find_notification_chains()
        for chain in notification_chains:
            if len(chain.notifications) >= 3:
                confidence = self._calculate_observer_confidence(chain)
                opportunity = self._create_observer_opportunity(chain, confidence)
                opportunities.append(opportunity)
        
        # Find manual listener iteration patterns
        listener_patterns = self._find_listener_patterns()
        for pattern in listener_patterns:
            confidence = 0.85
            opportunity = self._create_formalize_observer_opportunity(pattern, confidence)
            opportunities.append(opportunity)
        
        self.opportunities = opportunities
        return opportunities
    
    def _find_notification_chains(self) -> List[NotificationChain]:
        """Find methods that notify multiple objects."""
        chains = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check for state modification
                    has_state_change = self._has_state_modification(node)
                    
                    if has_state_change:
                        # Count external method calls
                        notifications = self._count_external_calls(node)
                        
                        if len(notifications) >= 2:
                            chains.append(NotificationChain(
                                file_path=file_path,
                                method_name=node.name,
                                line_number=node.lineno,
                                notifications=notifications,
                                has_state_change=True
                            ))
        
        return chains
    
    def _has_state_modification(self, func_node: ast.FunctionDef) -> bool:
        """Check if function modifies self attributes."""
        for node in ast.walk(func_node):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Attribute):
                        if isinstance(target.value, ast.Name) and target.value.id == 'self':
                            return True
        return False
    
    def _count_external_calls(self, func_node: ast.FunctionDef) -> List[str]:
        """Count method calls to external objects."""
        calls = []
        
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    # Check if calling method on another object
                    if isinstance(node.func.value, ast.Attribute):
                        if isinstance(node.func.value.value, ast.Name):
                            if node.func.value.value.id == 'self':
                                obj_attr = node.func.value.attr
                                method = node.func.attr
                                calls.append(f"{obj_attr}.{method}()")
        
        return calls
    
    def _find_listener_patterns(self) -> List[dict]:
        """Find manual listener list iteration patterns."""
        patterns = []
        
        for file_path, parsed_file in self.context.parsed_files.items():
            for node in ast.walk(parsed_file.ast_root):
                if isinstance(node, ast.ClassDef):
                    # Look for listener/observer list attributes
                    has_listener_list = False
                    has_manual_iteration = False
                    
                    for class_node in ast.walk(node):
                        # Check for __init__ with listener list
                        if isinstance(class_node, ast.FunctionDef) and class_node.name == '__init__':
                            for stmt in class_node.body:
                                if isinstance(stmt, ast.Assign):
                                    for target in stmt.targets:
                                        if isinstance(target, ast.Attribute):
                                            attr_name = target.attr
                                            if any(keyword in attr_name.lower() 
                                                   for keyword in ['listener', 'observer', 'callback', 'handler']):
                                                has_listener_list = True
                        
                        # Check for manual iteration
                        if isinstance(class_node, ast.For):
                            if isinstance(class_node.iter, ast.Attribute):
                                attr_name = class_node.iter.attr
                                if any(keyword in attr_name.lower() 
                                       for keyword in ['listener', 'observer', 'callback', 'handler']):
                                    has_manual_iteration = True
                    
                    if has_listener_list and has_manual_iteration:
                        patterns.append({
                            'file_path': file_path,
                            'class_name': node.name,
                            'line_number': node.lineno
                        })
        
        return patterns
    
    def _calculate_observer_confidence(self, chain: NotificationChain) -> float:
        """Calculate confidence for Observer opportunity."""
        confidence = 0.6
        
        if len(chain.notifications) >= 4:
            confidence += 0.3
        elif len(chain.notifications) >= 3:
            confidence += 0.2
        
        if chain.has_state_change:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _create_observer_opportunity(
        self, 
        chain: NotificationChain, 
        confidence: float
    ) -> PatternOpportunity:
        """Create PatternOpportunity for Observer pattern."""
        description = (
            f"Method '{chain.method_name}' notifies {len(chain.notifications)} objects "
            f"after state change: {', '.join(chain.notifications[:3])}"
        )
        
        benefit = (
            "Decouples subject from observers, enables dynamic subscription, "
            "supports multiple observers without tight coupling"
        )
        
        example = f"""# Before: Direct notifications
# def {chain.method_name}(self):
#     self.state = new_value
#     {chain.notifications[0]}
#     {chain.notifications[1] if len(chain.notifications) > 1 else ''}

# After: Observer pattern
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer: Observer):
        self._observers.append(observer)
    
    def notify(self):
        for observer in self._observers:
            observer.update(self)

# Usage
subject.attach(observer1)
subject.attach(observer2)
subject.notify()  # All observers updated automatically
"""
        
        return self._create_opportunity(
            file_path=chain.file_path,
            line_number=chain.line_number,
            confidence=confidence,
            description=description,
            trigger_type="Direct Notifications",
            benefit=benefit,
            example_code=example,
            evidence={
                'notification_count': len(chain.notifications),
                'method_name': chain.method_name,
                'notifications': chain.notifications
            }
        )
    
    def _create_formalize_observer_opportunity(
        self, 
        pattern: dict, 
        confidence: float
    ) -> PatternOpportunity:
        """Create opportunity for formalizing existing observer-like pattern."""
        description = (
            f"Class '{pattern['class_name']}' has manual listener iteration. "
            f"Consider formalizing with Observer pattern interface"
        )
        
        benefit = "Standardizes notification mechanism, improves maintainability"
        
        return self._create_opportunity(
            file_path=pattern['file_path'],
            line_number=pattern['line_number'],
            confidence=confidence,
            description=description,
            trigger_type="Manual Listener Iteration",
            benefit=benefit,
            example_code="",
            evidence=pattern
        )

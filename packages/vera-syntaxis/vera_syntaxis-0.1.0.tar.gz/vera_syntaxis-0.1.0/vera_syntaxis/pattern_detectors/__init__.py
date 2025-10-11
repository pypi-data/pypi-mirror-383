"""Design Pattern Detection Module.

This module detects opportunities to apply design patterns in Python codebases.
"""

from vera_syntaxis.pattern_detectors.base import (
    BasePatternDetector,
    PatternOpportunity,
    PATTERN_REGISTRY
)
from vera_syntaxis.pattern_detectors.factory_detector import FactoryDetector
from vera_syntaxis.pattern_detectors.strategy_detector import StrategyDetector
from vera_syntaxis.pattern_detectors.observer_detector import ObserverDetector
from vera_syntaxis.pattern_detectors.singleton_detector import SingletonDetector
from vera_syntaxis.pattern_detectors.decorator_detector import DecoratorPatternDetector
from vera_syntaxis.pattern_detectors.adapter_detector import AdapterDetector

# Register detectors
PATTERN_REGISTRY['factory'] = FactoryDetector
PATTERN_REGISTRY['strategy'] = StrategyDetector
PATTERN_REGISTRY['observer'] = ObserverDetector
PATTERN_REGISTRY['singleton'] = SingletonDetector
PATTERN_REGISTRY['decorator'] = DecoratorPatternDetector
PATTERN_REGISTRY['adapter'] = AdapterDetector

__all__ = [
    'BasePatternDetector',
    'PatternOpportunity',
    'FactoryDetector',
    'StrategyDetector',
    'ObserverDetector',
    'SingletonDetector',
    'DecoratorPatternDetector',
    'AdapterDetector',
    'PATTERN_REGISTRY',
    'run_all_detectors'
]


def run_all_detectors(context) -> list:
    """
    Run all registered pattern detectors.
    
    Args:
        context: LinterContext with parsed files, symbol table, etc.
    
    Returns:
        List of PatternOpportunity objects
    """
    all_opportunities = []
    
    for name, detector_cls in PATTERN_REGISTRY.items():
        detector = detector_cls(context)
        opportunities = detector.detect()
        all_opportunities.extend(opportunities)
    
    return all_opportunities

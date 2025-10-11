"""Base classes for pattern detection."""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)

# Pattern detector registry
PATTERN_REGISTRY: Dict[str, type] = {}


@dataclass
class PatternOpportunity:
    """Represents a detected design pattern opportunity."""
    
    pattern_name: str           # e.g., "Factory Method", "Strategy"
    file_path: Path
    line_number: int
    confidence: float           # 0.0-1.0
    description: str            # Human-readable explanation
    trigger_type: str           # Code smell that triggered detection
    benefit: str                # Expected improvement from applying pattern
    example_code: Optional[str] = None  # Suggested refactoring example
    related_files: List[Path] = field(default_factory=list)  # Other affected files
    evidence: Dict = field(default_factory=dict)  # Detection evidence for debugging
    
    def __str__(self) -> str:
        """String representation for display."""
        return (f"[{self.pattern_name}] {self.file_path}:{self.line_number} - "
                f"{self.description} (confidence: {self.confidence:.0%})")


class BasePatternDetector(ABC):
    """Abstract base class for pattern detectors."""
    
    def __init__(self, context):
        """
        Initialize pattern detector.
        
        Args:
            context: LinterContext with parsed files, symbol table, call graph, etc.
        """
        self.context = context
        self.opportunities: List[PatternOpportunity] = []
    
    @property
    @abstractmethod
    def pattern_name(self) -> str:
        """Name of the design pattern this detector finds."""
        pass
    
    @property
    @abstractmethod
    def pattern_description(self) -> str:
        """Short description of when this pattern should be used."""
        pass
    
    @abstractmethod
    def detect(self) -> List[PatternOpportunity]:
        """
        Run detection logic and return opportunities.
        
        Returns:
            List of PatternOpportunity objects
        """
        pass
    
    def _calculate_confidence(self, evidence: Dict) -> float:
        """
        Calculate confidence score based on evidence.
        
        Override in subclasses for pattern-specific logic.
        
        Args:
            evidence: Dictionary of detection evidence
        
        Returns:
            Confidence score between 0.0 and 1.0
        """
        return 0.5  # Default medium confidence
    
    def _create_opportunity(
        self,
        file_path: Path,
        line_number: int,
        confidence: float,
        description: str,
        trigger_type: str,
        benefit: str,
        example_code: Optional[str] = None,
        related_files: Optional[List[Path]] = None,
        evidence: Optional[Dict] = None
    ) -> PatternOpportunity:
        """
        Helper to create PatternOpportunity with common fields filled.
        
        Args:
            file_path: File where opportunity detected
            line_number: Line number in file
            confidence: Confidence score (0.0-1.0)
            description: Human-readable description
            trigger_type: What triggered detection
            benefit: Expected benefit
            example_code: Optional example refactoring
            related_files: Optional list of related files
            evidence: Optional evidence dictionary
        
        Returns:
            PatternOpportunity instance
        """
        return PatternOpportunity(
            pattern_name=self.pattern_name,
            file_path=file_path,
            line_number=line_number,
            confidence=confidence,
            description=description,
            trigger_type=trigger_type,
            benefit=benefit,
            example_code=example_code,
            related_files=related_files or [],
            evidence=evidence or {}
        )

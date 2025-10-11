"""Base classes and registry for architectural linters."""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict
import networkx as nx  # type: ignore

from vera_syntaxis.config import VeraSyntaxisConfig
from vera_syntaxis.symbol_table import SymbolTable
from vera_syntaxis.violations import Violation
from vera_syntaxis.parser import ASTParser, ParsedFile

logger = logging.getLogger(__name__)


class LinterContext:
    """Provides all necessary context for a linter to perform its analysis."""
    def __init__(
        self,
        config: VeraSyntaxisConfig,
        parser: ASTParser,
        symbol_table: SymbolTable,
        call_graph: nx.DiGraph,
        parsed_files: Dict[Path, ParsedFile]
    ):
        self.config = config
        self.parser = parser
        self.symbol_table = symbol_table
        self.call_graph = call_graph
        self.parsed_files = parsed_files


class BaseLinter(ABC):
    """Abstract base class for all architectural linters."""

    def __init__(self, context: LinterContext):
        self.context = context
        self.violations: List[Violation] = []

    @property
    @abstractmethod
    def rule_id(self) -> str:
        """A unique identifier for the rule this linter enforces."""
        pass

    @abstractmethod
    def run(self) -> None:
        """Execute the linting check."""
        pass

    def add_violation(self, violation: Violation):
        """Add a violation to the list of findings."""
        self.violations.append(violation)
        logger.debug(f"Violation added: {violation}")


# A simple registry to hold all available linters
LINTER_REGISTRY: Dict[str, type] = {}


def register_linter(name: str):
    """
A decorator to register a linter class in the registry.
    """
    def decorator(linter_class):
        if not issubclass(linter_class, BaseLinter):
            raise TypeError("Registered linter must inherit from BaseLinter.")
        LINTER_REGISTRY[name] = linter_class
        logger.debug(f"Linter registered: {name}")
        return linter_class
    return decorator


def run_all_linters(context: LinterContext) -> List[Violation]:
    """
    Initialize and run all registered linters.

    Args:
        context: The LinterContext containing all necessary analysis components.

    Returns:
        A list of all violations found by all linters.
    """
    all_violations: List[Violation] = []
    logger.info(f"Running {len(LINTER_REGISTRY)} registered linters.")

    for name, linter_class in LINTER_REGISTRY.items():
        logger.info(f"Running linter: {name}")
        linter = linter_class(context)
        linter.run()
        all_violations.extend(linter.violations)

    logger.info(f"Found {len(all_violations)} total violations.")
    return all_violations

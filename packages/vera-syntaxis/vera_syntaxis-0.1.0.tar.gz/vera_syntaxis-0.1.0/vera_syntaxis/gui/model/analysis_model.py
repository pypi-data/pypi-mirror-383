"""Analysis Model - manages analysis state and results."""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

from vera_syntaxis.file_discovery import discover_python_files
from vera_syntaxis.parser import ASTParser
from vera_syntaxis.symbol_table import SymbolTable, SymbolTableBuilder
from vera_syntaxis.call_graph import build_call_graph
from vera_syntaxis.linter_base import LinterContext, LINTER_REGISTRY
from vera_syntaxis.config import load_config
from vera_syntaxis.violations import Violation

# Import all linters to register them
import vera_syntaxis.linters  # noqa: F401


class AnalysisStatus(Enum):
    """Analysis status states."""
    IDLE = "idle"
    SCANNING = "scanning"
    PARSING = "parsing"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class AnalysisResult:
    """Container for analysis results."""
    violations: List[Violation] = field(default_factory=list)
    pattern_opportunities: List = field(default_factory=list)  # List[PatternOpportunity]
    file_count: int = 0
    error_count: int = 0
    status: AnalysisStatus = AnalysisStatus.IDLE
    error_message: Optional[str] = None


class AnalysisModel:
    """Model for managing Vera Syntaxis analysis."""
    
    def __init__(self):
        """Initialize the analysis model."""
        self.project_path: Optional[Path] = None
        self.result: AnalysisResult = AnalysisResult()
        self._cancel_requested: bool = False
        
    def set_project_path(self, path: Path) -> bool:
        """
        Set the project path to analyze.
        
        Args:
            path: Path to project directory
            
        Returns:
            True if path is valid, False otherwise
        """
        if not path.exists() or not path.is_dir():
            return False
        
        self.project_path = path
        return True
    
    def request_cancel(self):
        """Request cancellation of current analysis."""
        self._cancel_requested = True
    
    def is_cancel_requested(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancel_requested
    
    def run_analysis(self, progress_callback=None) -> AnalysisResult:
        """
        Run Vera Syntaxis analysis on the project.
        
        Args:
            progress_callback: Optional callback function(status, message, percent)
            
        Returns:
            AnalysisResult with violations and status
        """
        self._cancel_requested = False
        self.result = AnalysisResult()
        
        if not self.project_path:
            self.result.status = AnalysisStatus.ERROR
            self.result.error_message = "No project path set"
            return self.result
        
        try:
            # Step 1: Discover files
            if progress_callback:
                progress_callback(AnalysisStatus.SCANNING, "Scanning for Python files...", 10)
            
            if self._cancel_requested:
                self.result.status = AnalysisStatus.CANCELLED
                return self.result
            
            python_files = discover_python_files(self.project_path)
            self.result.file_count = len(python_files)
            
            if not python_files:
                self.result.status = AnalysisStatus.COMPLETE
                return self.result
            
            # Step 2: Parse files
            if progress_callback:
                progress_callback(AnalysisStatus.PARSING, f"Parsing {len(python_files)} files...", 30)
            
            if self._cancel_requested:
                self.result.status = AnalysisStatus.CANCELLED
                return self.result
            
            parser = ASTParser(self.project_path)
            parsed_files = parser.parse_files(python_files)
            
            # Step 3: Build symbol table and call graph
            if progress_callback:
                progress_callback(AnalysisStatus.PARSING, "Building symbol table...", 50)
            
            if self._cancel_requested:
                self.result.status = AnalysisStatus.CANCELLED
                return self.result
            
            symbol_table = SymbolTable()
            for file_path, parsed_file in parsed_files.items():
                symbol_builder = SymbolTableBuilder(file_path, self.project_path, symbol_table)
                symbol_builder.visit(parsed_file.ast_root)
            
            call_graph = build_call_graph(parser, symbol_table, parsed_files)
            
            # Step 4: Load configuration
            config = load_config(self.project_path)
            
            # Step 5: Run linters
            if progress_callback:
                progress_callback(AnalysisStatus.ANALYZING, "Running linters...", 70)
            
            if self._cancel_requested:
                self.result.status = AnalysisStatus.CANCELLED
                return self.result
            
            context = LinterContext(
                parsed_files=parsed_files,
                symbol_table=symbol_table,
                call_graph=call_graph,
                parser=parser,
                config=config
            )
            
            for name, linter_cls in LINTER_REGISTRY.items():
                if self._cancel_requested:
                    self.result.status = AnalysisStatus.CANCELLED
                    return self.result
                
                linter = linter_cls(context)
                linter.run()
                self.result.violations.extend(linter.violations)
            
            # Step 6: Run pattern detectors
            if progress_callback:
                progress_callback(AnalysisStatus.ANALYZING, "Detecting pattern opportunities...", 85)
            
            if self._cancel_requested:
                self.result.status = AnalysisStatus.CANCELLED
                return self.result
            
            try:
                from vera_syntaxis.pattern_detectors import run_all_detectors
                pattern_opportunities = run_all_detectors(context)
                self.result.pattern_opportunities = pattern_opportunities
            except Exception as e:
                # Don't fail entire analysis if pattern detection fails
                import logging
                logging.getLogger(__name__).warning(f"Pattern detection failed: {e}")
                self.result.pattern_opportunities = []
            
            # Complete
            if progress_callback:
                progress_callback(AnalysisStatus.COMPLETE, 
                                f"Analysis complete: {len(self.result.violations)} violations, "
                                f"{len(self.result.pattern_opportunities)} pattern opportunities", 100)
            
            self.result.status = AnalysisStatus.COMPLETE
            
        except Exception as e:
            self.result.status = AnalysisStatus.ERROR
            self.result.error_message = str(e)
            self.result.error_count = 1
            
        return self.result
    
    def get_violations_by_rule(self) -> Dict[str, List[Violation]]:
        """
        Group violations by rule ID.
        
        Returns:
            Dictionary mapping rule_id to list of violations
        """
        violations_by_rule = {}
        for violation in self.result.violations:
            rule_id = violation.rule_id
            if rule_id not in violations_by_rule:
                violations_by_rule[rule_id] = []
            violations_by_rule[rule_id].append(violation)
        return violations_by_rule
    
    def get_violations_by_file(self) -> Dict[Path, List[Violation]]:
        """
        Group violations by file path.
        
        Returns:
            Dictionary mapping file path to list of violations
        """
        violations_by_file = {}
        for violation in self.result.violations:
            file_path = violation.file_path
            if file_path not in violations_by_file:
                violations_by_file[file_path] = []
            violations_by_file[file_path].append(violation)
        return violations_by_file

"""Tests for the AnalysisModel class."""

import pytest
from pathlib import Path
import sys
import ast

# Add parent directory to path to import model and vera_syntaxis
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "Main"))

from model.analysis_model import AnalysisModel, AnalysisStatus


def test_analysis_model_initialization():
    """Test that AnalysisModel can be initialized."""
    model = AnalysisModel()
    assert model.project_path is None
    assert model.result.status == AnalysisStatus.IDLE
    assert len(model.result.violations) == 0


def test_set_project_path_valid(temp_project_dir: Path):
    """Test setting a valid project path."""
    model = AnalysisModel()
    result = model.set_project_path(temp_project_dir)
    assert result is True
    assert model.project_path == temp_project_dir


def test_set_project_path_invalid():
    """Test setting an invalid project path."""
    model = AnalysisModel()
    invalid_path = Path("/nonexistent/path")
    result = model.set_project_path(invalid_path)
    assert result is False


def test_run_analysis_no_project_path():
    """Test running analysis without setting project path."""
    model = AnalysisModel()
    result = model.run_analysis()
    assert result.status == AnalysisStatus.ERROR
    assert result.error_message == "No project path set"


def test_symbol_table_builder_instantiation_is_correct(sample_project: Path):
    """Test that SymbolTableBuilder is instantiated with correct arguments - regression test for bug."""
    from vera_syntaxis.file_discovery import discover_python_files
    from vera_syntaxis.parser import ASTParser
    from vera_syntaxis.symbol_table import SymbolTable, SymbolTableBuilder
    
    # Discover and parse files
    python_files = discover_python_files(sample_project)
    parser = ASTParser(sample_project)
    parsed_files = parser.parse_files(python_files)
    
    # This is the code pattern that was broken - verify it works now
    symbol_table = SymbolTable()
    for file_path, parsed_file in parsed_files.items():
        # This should NOT raise TypeError about missing positional arguments
        try:
            symbol_builder = SymbolTableBuilder(file_path, sample_project, symbol_table)
            symbol_builder.visit(parsed_file.ast_root)
        except TypeError as e:
            if "missing" in str(e) and "positional" in str(e):
                pytest.fail(f"SymbolTableBuilder instantiation failed with: {e}")
            raise
    
    # Verify symbols were added
    assert len(symbol_table) > 0

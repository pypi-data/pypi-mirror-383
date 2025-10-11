"""Tests for file discovery module."""

import pytest
from pathlib import Path
from vera_syntaxis.file_discovery import (
    discover_python_files,
    is_ignored_directory,
    DEFAULT_IGNORE_DIRS
)


def test_discover_python_files_in_simple_project(sample_project: Path):
    """Test discovering Python files in a simple project structure."""
    files = discover_python_files(sample_project)
    
    # Should find files in src/ and tests/ but not in __pycache__ or .venv
    file_names = {f.name for f in files}
    
    assert "__init__.py" in file_names
    assert "main.py" in file_names
    assert "user.py" in file_names
    assert "test_user.py" in file_names
    
    # Should not find files in ignored directories
    assert "cache.pyc" not in file_names
    assert "lib.py" not in file_names


def test_discover_python_files_counts(sample_project: Path):
    """Test that the correct number of files are discovered."""
    files = discover_python_files(sample_project)
    
    # Should find: src/__init__.py, src/main.py, src/models/__init__.py,
    # src/models/user.py, src/views/__init__.py, tests/test_user.py
    assert len(files) == 6


def test_discover_python_files_with_custom_ignore(sample_project: Path):
    """Test file discovery with custom ignore directories."""
    # Ignore tests directory
    files = discover_python_files(sample_project, ignore_dirs={'tests', '__pycache__', '.venv'})
    
    file_names = {f.name for f in files}
    assert "test_user.py" not in file_names
    assert "main.py" in file_names


def test_discover_python_files_nonexistent_path(temp_project_dir: Path):
    """Test that ValueError is raised for nonexistent path."""
    nonexistent = temp_project_dir / "does_not_exist"
    
    with pytest.raises(ValueError, match="does not exist"):
        discover_python_files(nonexistent)


def test_discover_python_files_file_not_directory(sample_python_file: Path):
    """Test that ValueError is raised when path is a file, not a directory."""
    with pytest.raises(ValueError, match="not a directory"):
        discover_python_files(sample_python_file)


def test_discover_python_files_empty_directory(temp_project_dir: Path):
    """Test discovering files in an empty directory."""
    files = discover_python_files(temp_project_dir)
    assert len(files) == 0


def test_is_ignored_directory():
    """Test the is_ignored_directory helper function."""
    ignore_dirs = {'__pycache__', '.venv'}
    
    # Test direct match
    assert is_ignored_directory(Path('__pycache__'), ignore_dirs)
    assert is_ignored_directory(Path('.venv'), ignore_dirs)
    
    # Test parent match
    assert is_ignored_directory(Path('__pycache__/file.py'), ignore_dirs)
    assert is_ignored_directory(Path('src/__pycache__/file.py'), ignore_dirs)
    
    # Test no match
    assert not is_ignored_directory(Path('src/models'), ignore_dirs)
    assert not is_ignored_directory(Path('tests'), ignore_dirs)


def test_default_ignore_dirs_includes_common_patterns():
    """Test that DEFAULT_IGNORE_DIRS includes common patterns."""
    assert '.venv' in DEFAULT_IGNORE_DIRS
    assert '__pycache__' in DEFAULT_IGNORE_DIRS
    assert '.git' in DEFAULT_IGNORE_DIRS
    assert 'node_modules' in DEFAULT_IGNORE_DIRS
    assert '.pytest_cache' in DEFAULT_IGNORE_DIRS

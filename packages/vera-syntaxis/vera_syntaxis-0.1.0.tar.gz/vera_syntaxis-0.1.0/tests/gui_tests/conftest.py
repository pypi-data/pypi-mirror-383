"""Pytest configuration and fixtures for Tools tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_project_dir() -> Generator[Path, None, None]:
    """
    Create a temporary project directory for testing.
    
    Yields:
        Path to temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_project(temp_project_dir: Path) -> Path:
    """
    Create a sample project structure for testing.
    
    Args:
        temp_project_dir: Temporary project directory
        
    Returns:
        Path to the project root
    """
    # Create directory structure
    (temp_project_dir / "src").mkdir()
    
    # Create Python files
    (temp_project_dir / "src" / "__init__.py").write_text("", encoding='utf-8')
    (temp_project_dir / "src" / "main.py").write_text("""
class MyClass:
    def __init__(self):
        self.value = 0
    
    def my_method(self, x: int) -> int:
        return x + self.value
""", encoding='utf-8')
    
    return temp_project_dir

"""Pytest configuration and fixtures for Vera Syntaxis tests."""

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
def sample_python_file(temp_project_dir: Path) -> Path:
    """
    Create a sample Python file for testing.
    
    Args:
        temp_project_dir: Temporary project directory
        
    Returns:
        Path to the created file
    """
    file_path = temp_project_dir / "sample.py"
    file_path.write_text("""
import os
from typing import List

class MyClass:
    def __init__(self):
        self.value = 0
    
    def my_method(self, x: int) -> int:
        return x + self.value
""", encoding='utf-8')
    return file_path


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
    (temp_project_dir / "src" / "models").mkdir()
    (temp_project_dir / "src" / "views").mkdir()
    (temp_project_dir / "tests").mkdir()
    (temp_project_dir / "__pycache__").mkdir()
    (temp_project_dir / ".venv").mkdir()
    
    # Create Python files
    (temp_project_dir / "src" / "__init__.py").write_text("", encoding='utf-8')
    (temp_project_dir / "src" / "main.py").write_text("""
import sys
from models.user import User

def main():
    user = User()
    print(user.name)
""", encoding='utf-8')
    
    (temp_project_dir / "src" / "models" / "__init__.py").write_text("", encoding='utf-8')
    (temp_project_dir / "src" / "models" / "user.py").write_text("""
class User:
    def __init__(self):
        self.name = "John"
""", encoding='utf-8')
    
    (temp_project_dir / "src" / "views" / "__init__.py").write_text("", encoding='utf-8')
    (temp_project_dir / "tests" / "test_user.py").write_text("""
def test_user():
    assert True
""", encoding='utf-8')
    
    # Create files that should be ignored
    (temp_project_dir / "__pycache__" / "cache.pyc").write_text("", encoding='utf-8')
    (temp_project_dir / ".venv" / "lib.py").write_text("", encoding='utf-8')
    
    return temp_project_dir

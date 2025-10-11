"""File discovery module for finding Python files in a project."""

import logging
from pathlib import Path
from typing import List, Set, Optional

logger = logging.getLogger(__name__)

# Default directories to ignore during file discovery
DEFAULT_IGNORE_DIRS: Set[str] = {
    '.venv',
    'venv',
    '__pycache__',
    '.git',
    '.svn',
    '.hg',
    'node_modules',
    '.tox',
    '.pytest_cache',
    '.mypy_cache',
    'build',
    'dist',
    '*.egg-info',
}


def discover_python_files(
    project_path: Path,
    ignore_dirs: Optional[Set[str]] = None
) -> List[Path]:
    """
    Recursively discover all Python files in a project directory.
    
    Args:
        project_path: Root directory to search for Python files
        ignore_dirs: Set of directory names to ignore (uses DEFAULT_IGNORE_DIRS if None)
        
    Returns:
        List of Path objects for all discovered .py files
        
    Raises:
        ValueError: If project_path does not exist or is not a directory
    """
    if not project_path.exists():
        raise ValueError(f"Project path does not exist: {project_path}")
    
    if not project_path.is_dir():
        raise ValueError(f"Project path is not a directory: {project_path}")
    
    # Use default ignore dirs if none provided
    if ignore_dirs is None:
        ignore_dirs = DEFAULT_IGNORE_DIRS
    
    python_files: List[Path] = []
    
    logger.info(f"Discovering Python files in: {project_path}")
    logger.debug(f"Ignoring directories: {ignore_dirs}")
    
    # Walk the directory tree
    for path in project_path.rglob("*.py"):
        # Check if any parent directory should be ignored
        should_ignore = False
        for parent in path.parents:
            if parent.name in ignore_dirs:
                should_ignore = True
                break
        
        if not should_ignore:
            python_files.append(path)
            logger.debug(f"Found Python file: {path}")
    
    logger.info(f"Discovered {len(python_files)} Python files")
    return python_files


def is_ignored_directory(path: Path, ignore_dirs: Set[str]) -> bool:
    """
    Check if a path or any of its parents should be ignored.
    
    Args:
        path: Path to check
        ignore_dirs: Set of directory names to ignore
        
    Returns:
        True if the path should be ignored, False otherwise
    """
    for parent in [path] + list(path.parents):
        if parent.name in ignore_dirs:
            return True
    return False

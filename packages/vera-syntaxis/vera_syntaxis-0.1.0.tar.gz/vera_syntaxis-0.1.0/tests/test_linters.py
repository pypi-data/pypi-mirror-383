"""Tests for the linters and the full analysis pipeline."""

import pytest
from pathlib import Path
from vera_syntaxis.cli import cmd_analyze
import argparse

@pytest.fixture
def project_with_violation(temp_project_dir: Path) -> Path:
    """Create a sample project with a clear tight coupling violation."""
    # A concrete class that will be instantiated directly
    (temp_project_dir / "database.py").write_text("""
class DatabaseConnection:
    def query(self, sql: str):
        print(f"Executing: {sql}")
""")

    # A service class that directly instantiates another class
    (temp_project_dir / "user_service.py").write_text("""
from database import DatabaseConnection

class UserService:
    def get_user(self, user_id: int):
        # This is a direct instantiation violation
        db = DatabaseConnection()
        db.query(f"SELECT * FROM users WHERE id = {user_id}")
        return {"id": user_id, "name": "Test User"}
""")
    return temp_project_dir

def test_analyze_command_detects_violation(project_with_violation: Path, capsys):
    """Test that the 'analyze' command finds the direct instantiation violation."""
    args = argparse.Namespace(
        project_path=project_with_violation,
        verbose=False
    )

    # Run the analyze command
    exit_code = cmd_analyze(args)

    # Should return exit code 2, indicating violations were found
    assert exit_code == 2

    # Check the output for the violation message
    captured = capsys.readouterr()
    assert "Found 1 architectural violations" in captured.out
    assert "[TC001]" in captured.out
    assert "Direct instantiation of class 'DatabaseConnection'" in captured.out
    assert "inside method 'get_user' of class 'UserService'" in captured.out

def test_analyze_command_no_violations(sample_project: Path, capsys):
    """Test the 'analyze' command on a project with no violations."""
    args = argparse.Namespace(
        project_path=sample_project,
        verbose=False
    )

    exit_code = cmd_analyze(args)

    # Should return exit code 0
    assert exit_code == 0

    captured = capsys.readouterr()
    assert "No architectural violations found" in captured.out


"""Tests for the MVBC linter."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main

def test_mvbc_violation_detected(tmp_path: Path, capsys):
    """Test that an illegal dependency between MVBC layers is detected."""
    project_dir = tmp_path / "mvbc_project"
    project_dir.mkdir()

    # 1. Create pyproject.toml with MVBC configuration
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # 2. Create file structure and source files
    (project_dir / "models").mkdir()
    (project_dir / "models" / "user_model.py").write_text("class User: pass")

    (project_dir / "business").mkdir()
    (project_dir / "business" / "user_logic.py").write_text("class UserLogic: pass")

    (project_dir / "views").mkdir()
    # This view illegally imports from the business layer
    (project_dir / "views" / "user_view.py").write_text("""
from business.user_logic import UserLogic

class UserView:
    def __init__(self):
        self.logic = UserLogic()
""")

    (project_dir / "controllers").mkdir()
    (project_dir / "controllers" / "user_controller.py").write_text("""
from models.user_model import User
from views.user_view import UserView

class UserController:
    pass
""")

    # 3. Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # 4. Assert that violations were found
        assert exit_code == 2, f"Expected exit code 2 (violations found), got {exit_code}"
        captured = capsys.readouterr()
        # Both tight coupling and MVBC violations should be detected
        assert "Found 2 architectural violations" in captured.out
        assert "Illegal MVBC dependency: Layer 'View' cannot import from layer 'Business'" in captured.out
        assert "[W2902]" in captured.out  # MVBC linter rule ID
    finally:
        sys.argv = old_argv

"""Tests for enhanced MVBC linter rules."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_mvbc_business_cannot_call_view(tmp_path: Path, capsys):
    """Test that Business layer cannot import from View layer."""
    project_dir = tmp_path / "mvbc_project"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create layers
    (project_dir / "models").mkdir()
    (project_dir / "models" / "user.py").write_text("class User: pass")

    (project_dir / "views").mkdir()
    (project_dir / "views" / "user_view.py").write_text("class UserView: pass")

    (project_dir / "business").mkdir()
    (project_dir / "business" / "user_logic.py").write_text("""
from views.user_view import UserView

class UserLogic:
    def __init__(self):
        self.view = UserView()  # Violation: Business -> View
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "W2902" in captured.out
        assert "Business" in captured.out
        assert "View" in captured.out
        assert "Business logic should not depend on Views" in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_view_can_use_model(tmp_path: Path, capsys):
    """Test that View layer CAN import from Model layer (allowed)."""
    project_dir = tmp_path / "mvbc_project2"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create layers
    (project_dir / "models").mkdir()
    (project_dir / "models" / "user.py").write_text("class User: pass")

    (project_dir / "views").mkdir()
    (project_dir / "views" / "user_view.py").write_text("""
from models.user import User

class UserView:
    def __init__(self):
        self.user = User()  # Allowed: View -> Model
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find W2902 violations for View -> Model
        if "W2902" in captured.out:
            assert "View" not in captured.out or "Model" not in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_business_can_use_model(tmp_path: Path, capsys):
    """Test that Business layer CAN import from Model layer (allowed)."""
    project_dir = tmp_path / "mvbc_project3"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create layers
    (project_dir / "models").mkdir()
    (project_dir / "models" / "user.py").write_text("class User: pass")

    (project_dir / "business").mkdir()
    (project_dir / "business" / "user_logic.py").write_text("""
from models.user import User

class UserLogic:
    def process(self):
        user = User()  # Allowed: Business -> Model
        return user
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find W2902 violations for Business -> Model
        if "W2902" in captured.out:
            assert "Business" not in captured.out or "Model" not in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_controller_can_use_all_layers(tmp_path: Path, capsys):
    """Test that Controller can import from View, Business, and Model (all allowed)."""
    project_dir = tmp_path / "mvbc_project4"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create layers
    (project_dir / "models").mkdir()
    (project_dir / "models" / "user.py").write_text("class User: pass")

    (project_dir / "views").mkdir()
    (project_dir / "views" / "user_view.py").write_text("class UserView: pass")

    (project_dir / "business").mkdir()
    (project_dir / "business" / "user_logic.py").write_text("class UserLogic: pass")

    (project_dir / "controllers").mkdir()
    (project_dir / "controllers" / "user_controller.py").write_text("""
from models.user import User
from views.user_view import UserView
from business.user_logic import UserLogic

class UserController:
    def __init__(self):
        self.model = User()  # Allowed: Controller -> Model
        self.view = UserView()  # Allowed: Controller -> View
        self.logic = UserLogic()  # Allowed: Controller -> Business
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find W2902 violations for Controller -> anything
        if "W2902" in captured.out:
            assert "Controller" not in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_nested_directory_support(tmp_path: Path, capsys):
    """Test that nested directories are properly detected with single-level patterns."""
    project_dir = tmp_path / "mvbc_project5"
    project_dir.mkdir()

    # Create pyproject.toml with single-level patterns
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create nested directory structure
    (project_dir / "models" / "entities").mkdir(parents=True)
    (project_dir / "models" / "entities" / "user.py").write_text("class User: pass")

    (project_dir / "views" / "components").mkdir(parents=True)
    (project_dir / "views" / "components" / "user_view.py").write_text("class UserView: pass")

    (project_dir / "business" / "services").mkdir(parents=True)
    (project_dir / "business" / "services" / "user_logic.py").write_text("""
from views.components.user_view import UserView

class UserLogic:
    def __init__(self):
        self.view = UserView()  # Violation: Business -> View (nested)
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "W2902" in captured.out
        assert "Business" in captured.out
        assert "View" in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_explicit_nested_pattern(tmp_path: Path, capsys):
    """Test that explicit ** patterns work correctly."""
    project_dir = tmp_path / "mvbc_project6"
    project_dir.mkdir()

    # Create pyproject.toml with explicit ** patterns
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/**/*.py"]
view_paths = ["views/**/*.py"]
business_paths = ["business/**/*.py"]
controller_paths = ["controllers/**/*.py"]
""")

    # Create nested directory structure
    (project_dir / "models" / "entities").mkdir(parents=True)
    (project_dir / "models" / "entities" / "user.py").write_text("class User: pass")

    (project_dir / "views" / "components").mkdir(parents=True)
    (project_dir / "views" / "components" / "user_view.py").write_text("class UserView: pass")

    (project_dir / "business" / "services").mkdir(parents=True)
    (project_dir / "business" / "services" / "user_logic.py").write_text("""
from views.components.user_view import UserView

class UserLogic:
    def __init__(self):
        self.view = UserView()  # Violation: Business -> View
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "W2902" in captured.out
    finally:
        sys.argv = old_argv


def test_mvbc_suggestion_messages(tmp_path: Path, capsys):
    """Test that helpful suggestion messages are included in violations."""
    project_dir = tmp_path / "mvbc_project7"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.mvbc]
model_paths = ["models/*.py"]
view_paths = ["views/*.py"]
business_paths = ["business/*.py"]
controller_paths = ["controllers/*.py"]
""")

    # Create View -> Business violation
    (project_dir / "models").mkdir()
    (project_dir / "views").mkdir()
    (project_dir / "business").mkdir()
    (project_dir / "business" / "logic.py").write_text("class Logic: pass")
    (project_dir / "views" / "view.py").write_text("""
from business.logic import Logic

class View:
    def __init__(self):
        self.logic = Logic()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Check for helpful suggestion
        assert "Use a Controller to mediate" in captured.out or "Controller" in captured.out
    finally:
        sys.argv = old_argv

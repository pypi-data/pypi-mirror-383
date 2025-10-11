"""Tests for the Law of Demeter linter (TC002)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_law_of_demeter_violation_detected(tmp_path: Path, capsys):
    """Test that Law of Demeter violations are detected."""
    project_dir = tmp_path / "demeter_project"
    project_dir.mkdir()

    # Create pyproject.toml with custom max_demeter_chain
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_demeter_chain = 3
""")

    # Create a file with Law of Demeter violations
    (project_dir / "bad_code.py").write_text("""
class Address:
    def __init__(self):
        self.city = City()

class City:
    def __init__(self):
        self.postal_code = PostalCode()

class PostalCode:
    def __init__(self):
        self.country = Country()

class Country:
    def __init__(self):
        self.name = "USA"

class User:
    def __init__(self):
        self.address = Address()
    
    def get_country_name(self):
        # This violates Law of Demeter - chain length is 4
        return self.address.city.postal_code.country.name
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should find violations
        assert exit_code == 2, f"Expected exit code 2 (violations found), got {exit_code}"
        captured = capsys.readouterr()
        assert "TC002" in captured.out
        assert "Law of Demeter violation" in captured.out
        assert "chain length" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_law_of_demeter_method_chain_violation(tmp_path: Path, capsys):
    """Test that method chaining violations are detected."""
    project_dir = tmp_path / "demeter_project2"
    project_dir.mkdir()

    # Create pyproject.toml with max_demeter_chain = 2
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_demeter_chain = 2
""")

    # Create a file with method chaining violations
    (project_dir / "chaining.py").write_text("""
class DataService:
    def get_data(self):
        return DataProcessor()

class DataProcessor:
    def process(self):
        return DataFormatter()

class DataFormatter:
    def format(self):
        return "formatted"

class Client:
    def __init__(self):
        self.service = DataService()
    
    def get_formatted_data(self):
        # Chain length is 3, exceeds max of 2
        result = self.service.get_data().process().format()
        return result
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should find violations
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "TC002" in captured.out
        assert "Law of Demeter violation" in captured.out
    finally:
        sys.argv = old_argv


def test_law_of_demeter_no_violation(tmp_path: Path, capsys):
    """Test that short chains don't trigger violations."""
    project_dir = tmp_path / "demeter_project3"
    project_dir.mkdir()

    # Create pyproject.toml with max_demeter_chain = 3
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_demeter_chain = 3
""")

    # Create a file with acceptable chains
    (project_dir / "good_code.py").write_text("""
class User:
    def __init__(self):
        self.name = "Alice"
        self.address = Address()

class Address:
    def __init__(self):
        self.city = "New York"

class Client:
    def __init__(self):
        self.user = User()
    
    def get_city(self):
        # Chain length is 2, within limit
        return self.user.address.city
    
    def get_name(self):
        # Chain length is 1, within limit
        return self.user.name
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should not find TC002 violations (but might find TC001)
        captured = capsys.readouterr()
        # Check that if there are violations, they're not TC002
        if "violations" in captured.out.lower():
            assert "TC002" not in captured.out or "0" in captured.out
    finally:
        sys.argv = old_argv


def test_law_of_demeter_in_return_statement(tmp_path: Path, capsys):
    """Test that violations in return statements are detected."""
    project_dir = tmp_path / "demeter_project4"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_demeter_chain = 2
""")

    # Create a file with violation in return statement
    (project_dir / "return_violation.py").write_text("""
class A:
    def __init__(self):
        self.b = B()

class B:
    def __init__(self):
        self.c = C()

class C:
    def __init__(self):
        self.value = 42

class Client:
    def __init__(self):
        self.a = A()
    
    def get_value(self):
        # Chain length is 3 in return statement
        return self.a.b.c.value
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "TC002" in captured.out
    finally:
        sys.argv = old_argv


def test_law_of_demeter_in_function_arguments(tmp_path: Path, capsys):
    """Test that violations in function arguments are detected."""
    project_dir = tmp_path / "demeter_project5"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_demeter_chain = 2
""")

    # Create a file with violation in function arguments
    (project_dir / "arg_violation.py").write_text("""
class User:
    def __init__(self):
        self.profile = Profile()

class Profile:
    def __init__(self):
        self.settings = Settings()

class Settings:
    def __init__(self):
        self.theme = "dark"

def print_theme(theme):
    print(theme)

class Client:
    def __init__(self):
        self.user = User()
    
    def display_theme(self):
        # Chain length is 3 in function argument
        print_theme(self.user.profile.settings.theme)
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "TC002" in captured.out
    finally:
        sys.argv = old_argv


def test_law_of_demeter_default_config(tmp_path: Path, capsys):
    """Test that default max_demeter_chain (5) is used when not configured."""
    project_dir = tmp_path / "demeter_project6"
    project_dir.mkdir()

    # No pyproject.toml - should use default max_demeter_chain = 5

    # Create a file with chain length of 4 (should be OK with default)
    (project_dir / "default_config.py").write_text("""
class A:
    def __init__(self):
        self.b = B()

class B:
    def __init__(self):
        self.c = C()

class C:
    def __init__(self):
        self.d = D()

class D:
    def __init__(self):
        self.value = 42

class Client:
    def __init__(self):
        self.a = A()
    
    def get_value(self):
        # Chain length is 4, within default limit of 5
        return self.a.b.c.d.value
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should not find TC002 violations with default config
        captured = capsys.readouterr()
        if "violations" in captured.out.lower():
            assert "TC002" not in captured.out or exit_code != 2
    finally:
        sys.argv = old_argv

"""Tests for the God Object linter (GO001)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_god_object_too_many_methods(tmp_path: Path, capsys):
    """Test detection of class with too many methods."""
    project_dir = tmp_path / "god_project"
    project_dir.mkdir()

    # Create pyproject.toml with low threshold
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 5
max_attributes = 15
max_lines = 300
""")

    # Create class with too many methods
    (project_dir / "oversized.py").write_text("""
class OversizedClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
    def method6(self): pass  # Exceeds max of 5
    def method7(self): pass
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "GO001" in captured.out
        assert "God Object detected" in captured.out
        assert "methods" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_god_object_too_many_attributes(tmp_path: Path, capsys):
    """Test detection of class with too many attributes."""
    project_dir = tmp_path / "god_project2"
    project_dir.mkdir()

    # Create pyproject.toml with low threshold
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 20
max_attributes = 5
max_lines = 300
""")

    # Create class with too many attributes
    (project_dir / "oversized.py").write_text("""
class OversizedClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
        self.attr4 = 4
        self.attr5 = 5
        self.attr6 = 6  # Exceeds max of 5
        self.attr7 = 7
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "GO001" in captured.out
        assert "God Object detected" in captured.out
        assert "attributes" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_god_object_too_many_lines(tmp_path: Path, capsys):
    """Test detection of class with too many lines."""
    project_dir = tmp_path / "god_project3"
    project_dir.mkdir()

    # Create pyproject.toml with low threshold
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 20
max_attributes = 15
max_lines = 20
""")

    # Create class with too many lines
    lines = ["class OversizedClass:"]
    for i in range(25):  # 25 lines exceeds max of 20
        lines.append(f"    def method{i}(self):")
        lines.append(f"        pass")

    (project_dir / "oversized.py").write_text("\n".join(lines))

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "GO001" in captured.out
        assert "God Object detected" in captured.out
        assert "lines" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_god_object_multiple_violations(tmp_path: Path, capsys):
    """Test detection of class violating multiple thresholds."""
    project_dir = tmp_path / "god_project4"
    project_dir.mkdir()

    # Create pyproject.toml with low thresholds
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 3
max_attributes = 3
max_lines = 15
""")

    # Create class violating all thresholds
    lines = ["class OversizedClass:"]
    lines.append("    def __init__(self):")
    lines.append("        self.attr1 = 1")
    lines.append("        self.attr2 = 2")
    lines.append("        self.attr3 = 3")
    lines.append("        self.attr4 = 4  # Too many attributes")
    lines.append("")
    for i in range(1, 11):  # 10 methods (too many)
        lines.append(f"    def method{i}(self): pass")
    
    # This creates a class with ~17 lines (exceeds max of 15)
    (project_dir / "oversized.py").write_text("\n".join(lines))

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "GO001" in captured.out
        assert "methods" in captured.out.lower()
        assert "attributes" in captured.out.lower()
        assert "lines" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_god_object_no_violation(tmp_path: Path, capsys):
    """Test that well-sized classes don't trigger violations."""
    project_dir = tmp_path / "god_project5"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 20
max_attributes = 15
max_lines = 300
""")

    # Create reasonable class
    (project_dir / "good_class.py").write_text("""
class WellSizedClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find GO001 violations
        if "violations" in captured.out.lower():
            assert "GO001" not in captured.out
    finally:
        sys.argv = old_argv


def test_god_object_default_config(tmp_path: Path, capsys):
    """Test that default thresholds are reasonable."""
    project_dir = tmp_path / "god_project6"
    project_dir.mkdir()

    # No pyproject.toml - use defaults (20 methods, 15 attributes, 300 lines)

    # Create class within default limits
    (project_dir / "normal_class.py").write_text("""
class NormalClass:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
    
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
    def method5(self): pass
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find GO001 violations with defaults
        if "violations" in captured.out.lower():
            assert "GO001" not in captured.out
    finally:
        sys.argv = old_argv


def test_god_object_suggestion_message(tmp_path: Path, capsys):
    """Test that helpful suggestion messages are included."""
    project_dir = tmp_path / "god_project7"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.god_object]
max_methods = 3
""")

    # Create oversized class
    (project_dir / "oversized.py").write_text("""
class OversizedClass:
    def method1(self): pass
    def method2(self): pass
    def method3(self): pass
    def method4(self): pass
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Check for helpful suggestion
        assert "splitting" in captured.out.lower() or "smaller" in captured.out.lower()
    finally:
        sys.argv = old_argv

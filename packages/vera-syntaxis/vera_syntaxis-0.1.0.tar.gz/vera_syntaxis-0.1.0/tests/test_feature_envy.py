"""Tests for the Feature Envy linter (FE001)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_feature_envy_detected(tmp_path: Path, capsys):
    """Test detection of feature envy."""
    project_dir = tmp_path / "envy_project"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.feature_envy]
envy_threshold = 0.5
min_accesses = 3
""")

    # Create classes with feature envy
    (project_dir / "envy.py").write_text("""
class Account:
    def __init__(self):
        self.balance = 0

class Transaction:
    def __init__(self):
        self.account = Account()
    
    def process(self):
        # Feature envy: uses account more than self
        self.account.balance += 100
        self.account.balance -= 50
        self.account.balance *= 1.1
        return self.account.balance
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "FE001" in captured.out
        assert "Feature Envy detected" in captured.out
        assert "account" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_feature_envy_no_violation(tmp_path: Path, capsys):
    """Test that methods using primarily self don't trigger violations."""
    project_dir = tmp_path / "envy_project2"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.feature_envy]
envy_threshold = 0.5
min_accesses = 3
""")

    # Create class without feature envy
    (project_dir / "good.py").write_text("""
class Account:
    def __init__(self):
        self.balance = 0
        self.transactions = []
    
    def deposit(self, amount):
        self.balance += amount
        self.transactions.append(amount)
        return self.balance
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find FE001 violations
        if "violations" in captured.out.lower():
            assert "FE001" not in captured.out
    finally:
        sys.argv = old_argv


def test_feature_envy_threshold_config(tmp_path: Path, capsys):
    """Test that threshold configuration works."""
    project_dir = tmp_path / "envy_project3"
    project_dir.mkdir()

    # Create pyproject.toml with high threshold (lenient)
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.feature_envy]
envy_threshold = 0.9
min_accesses = 3
""")

    # Create class with moderate external access
    (project_dir / "moderate.py").write_text("""
class Printer:
    def __init__(self):
        pass

class Report:
    def __init__(self):
        self.data = []
        self.printer = Printer()
    
    def generate(self):
        self.data.append("line1")
        self.data.append("line2")
        self.printer.print()  # Only 1 external access vs 2 internal
        return self.data
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # With high threshold (0.9), shouldn't trigger (external ratio is only 0.33)
        if "violations" in captured.out.lower():
            assert "FE001" not in captured.out
    finally:
        sys.argv = old_argv


def test_feature_envy_min_accesses(tmp_path: Path, capsys):
    """Test that min_accesses prevents false positives on small methods."""
    project_dir = tmp_path / "envy_project4"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.feature_envy]
envy_threshold = 0.5
min_accesses = 5
""")

    # Create class with few accesses
    (project_dir / "small.py").write_text("""
class Logger:
    def log(self): pass

class Service:
    def __init__(self):
        self.logger = Logger()
    
    def run(self):
        # Only 2 total accesses (below min_accesses)
        self.logger.log()
        self.logger.log()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not trigger because total accesses < min_accesses
        if "violations" in captured.out.lower():
            assert "FE001" not in captured.out
    finally:
        sys.argv = old_argv


def test_feature_envy_skips_magic_methods(tmp_path: Path, capsys):
    """Test that magic methods like __init__ are skipped."""
    project_dir = tmp_path / "envy_project5"
    project_dir.mkdir()

    # Create class with external access in __init__
    (project_dir / "magic.py").write_text("""
class Database:
    def connect(self): pass

class Service:
    def __init__(self, db):
        # __init__ should be skipped even with external access
        db.connect()
        db.connect()
        db.connect()
        db.connect()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not trigger for __init__
        if "violations" in captured.out.lower():
            assert "FE001" not in captured.out
    finally:
        sys.argv = old_argv


def test_feature_envy_suggestion_message(tmp_path: Path, capsys):
    """Test that helpful suggestion messages are included."""
    project_dir = tmp_path / "envy_project6"
    project_dir.mkdir()

    # Create class with feature envy
    (project_dir / "envy.py").write_text("""
class Customer:
    def __init__(self):
        self.name = ""

class OrderProcessor:
    def __init__(self):
        self.customer = Customer()
    
    def validate_customer(self):
        # Feature envy: should be in Customer class
        result = self.customer.name
        result = self.customer.name.strip()
        result = self.customer.name.lower()
        result = self.customer.name.upper()
        return result
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Check for helpful suggestion
        assert "moving" in captured.out.lower() or "move" in captured.out.lower()
    finally:
        sys.argv = old_argv

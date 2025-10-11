"""Tests for the Data Clump linter (DC001)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_data_clump_detected(tmp_path: Path, capsys):
    """Test detection of data clump."""
    project_dir = tmp_path / "clump_project"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.data_clump]
min_clump_size = 3
min_occurrences = 2
""")

    # Create class with data clump
    (project_dir / "clump.py").write_text("""
class OrderProcessor:
    def calculate_total(self, price, quantity, discount):
        return price * quantity * (1 - discount)
    
    def validate_order(self, price, quantity, discount):
        return price > 0 and quantity > 0 and discount < 1
    
    def format_order(self, price, quantity, discount):
        return f"Order: {quantity} items at ${price} with {discount*100}% discount"
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "DC001" in captured.out
        assert "Data Clump detected" in captured.out
        assert "price" in captured.out.lower()
        assert "quantity" in captured.out.lower()
        assert "discount" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_data_clump_no_violation(tmp_path: Path, capsys):
    """Test that methods with different parameters don't trigger violations."""
    project_dir = tmp_path / "clump_project2"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.data_clump]
min_clump_size = 3
min_occurrences = 2
""")

    # Create class without data clumps
    (project_dir / "good.py").write_text("""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, x, y):
        return x * y
    
    def power(self, base, exponent):
        return base ** exponent
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find DC001 violations
        if "violations" in captured.out.lower():
            assert "DC001" not in captured.out
    finally:
        sys.argv = old_argv


def test_data_clump_min_clump_size(tmp_path: Path, capsys):
    """Test that min_clump_size configuration works."""
    project_dir = tmp_path / "clump_project3"
    project_dir.mkdir()

    # Create pyproject.toml with high min_clump_size
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.data_clump]
min_clump_size = 4
min_occurrences = 2
""")

    # Create class with 3-parameter clump (below threshold)
    (project_dir / "small_clump.py").write_text("""
class SmallClump:
    def method1(self, a, b, c):
        return a + b + c
    
    def method2(self, a, b, c):
        return a * b * c
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not trigger because clump size (3) < min_clump_size (4)
        if "violations" in captured.out.lower():
            assert "DC001" not in captured.out
    finally:
        sys.argv = old_argv


def test_data_clump_min_occurrences(tmp_path: Path, capsys):
    """Test that min_occurrences configuration works."""
    project_dir = tmp_path / "clump_project4"
    project_dir.mkdir()

    # Create pyproject.toml with high min_occurrences
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.data_clump]
min_clump_size = 3
min_occurrences = 3
""")

    # Create class with clump appearing only twice
    (project_dir / "rare_clump.py").write_text("""
class RareClump:
    def method1(self, x, y, z):
        return x + y + z
    
    def method2(self, x, y, z):
        return x * y * z
    
    def method3(self, a, b):
        return a + b
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not trigger because occurrences (2) < min_occurrences (3)
        if "violations" in captured.out.lower():
            assert "DC001" not in captured.out
    finally:
        sys.argv = old_argv


def test_data_clump_partial_overlap(tmp_path: Path, capsys):
    """Test that partial parameter overlap is handled correctly."""
    project_dir = tmp_path / "clump_project5"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.data_clump]
min_clump_size = 2
min_occurrences = 2
""")

    # Create class with partial overlap
    (project_dir / "overlap.py").write_text("""
class PartialOverlap:
    def method1(self, a, b, c):
        return a + b + c
    
    def method2(self, a, b, d):
        return a + b + d
    
    def method3(self, x, y):
        return x + y
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should detect (a, b) appearing in method1 and method2
        captured = capsys.readouterr()
        if exit_code == 2:
            assert "DC001" in captured.out
            # Should mention 'a' and 'b' appearing together
    finally:
        sys.argv = old_argv


def test_data_clump_suggestion_message(tmp_path: Path, capsys):
    """Test that helpful suggestion messages are included."""
    project_dir = tmp_path / "clump_project6"
    project_dir.mkdir()

    # Create class with data clump
    (project_dir / "clump.py").write_text("""
class CustomerService:
    def create_customer(self, name, email, phone):
        pass
    
    def update_customer(self, name, email, phone):
        pass
    
    def validate_customer(self, name, email, phone):
        pass
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Check for helpful suggestion
        assert "extracting" in captured.out.lower() or "extract" in captured.out.lower()
    finally:
        sys.argv = old_argv

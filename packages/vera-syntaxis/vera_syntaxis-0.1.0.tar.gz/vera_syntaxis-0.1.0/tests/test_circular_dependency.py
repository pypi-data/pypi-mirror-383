"""Tests for the Circular Dependency linter (CD001)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_circular_dependency_simple_cycle(tmp_path: Path, capsys):
    """Test detection of a simple A -> B -> A cycle."""
    project_dir = tmp_path / "circular_project"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.circular]
allow_self_cycles = false
""")

    # Create circular dependency: A.method_a -> B.method_b -> A.method_a
    (project_dir / "module_a.py").write_text("""
class ClassA:
    def method_a(self):
        from module_b import ClassB
        b = ClassB()
        b.method_b()
""")

    (project_dir / "module_b.py").write_text("""
class ClassB:
    def method_b(self):
        from module_a import ClassA
        a = ClassA()
        a.method_a()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "CD001" in captured.out
        assert "Circular dependency detected" in captured.out
    finally:
        sys.argv = old_argv


def test_circular_dependency_three_way_cycle(tmp_path: Path, capsys):
    """Test detection of A -> B -> C -> A cycle."""
    project_dir = tmp_path / "circular_project2"
    project_dir.mkdir()

    # Create circular dependency: A -> B -> C -> A
    (project_dir / "service_a.py").write_text("""
from service_b import ServiceB

class ServiceA:
    def process(self):
        b = ServiceB()
        return b.process()
""")

    (project_dir / "service_b.py").write_text("""
from service_c import ServiceC

class ServiceB:
    def process(self):
        c = ServiceC()
        return c.process()
""")

    (project_dir / "service_c.py").write_text("""
from service_a import ServiceA

class ServiceC:
    def process(self):
        a = ServiceA()
        return a.process()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        assert "CD001" in captured.out
        assert "Circular dependency detected" in captured.out
        assert "3 components" in captured.out
    finally:
        sys.argv = old_argv


def test_circular_dependency_self_cycle(tmp_path: Path, capsys):
    """Test that method-level recursion is not reported as a module cycle."""
    project_dir = tmp_path / "circular_project3"
    project_dir.mkdir()

    # Create pyproject.toml with allow_self_cycles = false
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.circular]
allow_self_cycles = false
""")

    # Create self-referential method (this is method-level recursion, not a module cycle)
    (project_dir / "recursive.py").write_text("""
class Calculator:
    def factorial(self, n):
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)  # Method recursion (not a module cycle)
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Method-level recursion is not a circular dependency at the module level
        # So we should not find CD001 violations
        captured = capsys.readouterr()
        assert "CD001" not in captured.out
    finally:
        sys.argv = old_argv


def test_circular_dependency_self_cycle_allowed(tmp_path: Path, capsys):
    """Test that self-cycles are allowed when configured."""
    project_dir = tmp_path / "circular_project4"
    project_dir.mkdir()

    # Create pyproject.toml with allow_self_cycles = true
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.circular]
allow_self_cycles = true
""")

    # Create self-referential method
    (project_dir / "recursive.py").write_text("""
class Calculator:
    def factorial(self, n):
        if n <= 1:
            return 1
        return n * self.factorial(n - 1)  # Self-cycle (allowed)
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find CD001 violations for self-cycles when allowed
        if "CD001" in captured.out:
            assert "Self-referential" not in captured.out
    finally:
        sys.argv = old_argv


def test_circular_dependency_no_cycle(tmp_path: Path, capsys):
    """Test that no violations are reported when there are no cycles."""
    project_dir = tmp_path / "circular_project5"
    project_dir.mkdir()

    # Create linear dependency: A -> B -> C (no cycle)
    (project_dir / "service_a.py").write_text("""
from service_b import ServiceB

class ServiceA:
    def process(self):
        b = ServiceB()
        return b.process()
""")

    (project_dir / "service_b.py").write_text("""
from service_c import ServiceC

class ServiceB:
    def process(self):
        c = ServiceC()
        return c.process()
""")

    (project_dir / "service_c.py").write_text("""
class ServiceC:
    def process(self):
        return "done"
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find CD001 violations
        if "violations" in captured.out.lower():
            assert "CD001" not in captured.out
    finally:
        sys.argv = old_argv


def test_circular_dependency_multiple_cycles(tmp_path: Path, capsys):
    """Test detection of multiple independent cycles."""
    project_dir = tmp_path / "circular_project6"
    project_dir.mkdir()

    # Create first cycle: A -> B -> A
    (project_dir / "pair_a.py").write_text("""
from pair_b import PairB

class PairA:
    def method(self):
        b = PairB()
        b.method()
""")

    (project_dir / "pair_b.py").write_text("""
from pair_a import PairA

class PairB:
    def method(self):
        a = PairA()
        a.method()
""")

    # Create second cycle: X -> Y -> X
    (project_dir / "pair_x.py").write_text("""
from pair_y import PairY

class PairX:
    def method(self):
        y = PairY()
        y.method()
""")

    (project_dir / "pair_y.py").write_text("""
from pair_x import PairX

class PairY:
    def method(self):
        x = PairX()
        x.method()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Should find multiple CD001 violations
        cd001_count = captured.out.count("CD001")
        assert cd001_count >= 2, f"Expected at least 2 CD001 violations, found {cd001_count}"
    finally:
        sys.argv = old_argv


def test_circular_dependency_suggestion_message(tmp_path: Path, capsys):
    """Test that helpful suggestion messages are included."""
    project_dir = tmp_path / "circular_project7"
    project_dir.mkdir()

    # Create circular dependency
    (project_dir / "module_a.py").write_text("""
from module_b import ClassB

class ClassA:
    def method(self):
        b = ClassB()
        b.method()
""")

    (project_dir / "module_b.py").write_text("""
from module_a import ClassA

class ClassB:
    def method(self):
        a = ClassA()
        a.method()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Check for helpful suggestions
        assert "interface" in captured.out.lower() or "dependency inversion" in captured.out.lower()
    finally:
        sys.argv = old_argv

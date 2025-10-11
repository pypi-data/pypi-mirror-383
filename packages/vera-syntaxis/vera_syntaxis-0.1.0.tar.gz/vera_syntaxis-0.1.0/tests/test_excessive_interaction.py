"""Tests for the Excessive Interaction linter (TC003)."""

import pytest
import sys
from pathlib import Path
from vera_syntaxis.cli import main


def test_excessive_interaction_violation_detected(tmp_path: Path, capsys):
    """Test that excessive interaction violations are detected."""
    project_dir = tmp_path / "interaction_project"
    project_dir.mkdir()

    # Create pyproject.toml with custom max_inter_class_calls
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_inter_class_calls = 3
""")

    # Create a file with excessive interactions
    (project_dir / "bad_code.py").write_text("""
class ServiceA:
    def method_a1(self):
        pass
    
    def method_a2(self):
        pass

class ServiceB:
    def method_b1(self):
        pass
    
    def method_b2(self):
        pass

class ServiceC:
    def method_c1(self):
        pass

class Client:
    def __init__(self):
        self.service_a = ServiceA()
        self.service_b = ServiceB()
        self.service_c = ServiceC()
    
    def do_work(self):
        # Calls 5 methods from other classes (exceeds max of 3)
        self.service_a.method_a1()
        self.service_a.method_a2()
        self.service_b.method_b1()
        self.service_b.method_b2()
        self.service_c.method_c1()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should find violations
        assert exit_code == 2, f"Expected exit code 2 (violations found), got {exit_code}"
        captured = capsys.readouterr()
        assert "TC003" in captured.out
        assert "Excessive interaction" in captured.out
        assert "exceeding maximum" in captured.out.lower()
    finally:
        sys.argv = old_argv


def test_excessive_interaction_no_violation(tmp_path: Path, capsys):
    """Test that classes within the limit don't trigger violations."""
    project_dir = tmp_path / "interaction_project2"
    project_dir.mkdir()

    # Create pyproject.toml with max_inter_class_calls = 5
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_inter_class_calls = 5
""")

    # Create a file with acceptable interactions
    (project_dir / "good_code.py").write_text("""
class ServiceA:
    def method_a1(self):
        pass
    
    def method_a2(self):
        pass

class ServiceB:
    def method_b1(self):
        pass

class Client:
    def __init__(self):
        self.service_a = ServiceA()
        self.service_b = ServiceB()
    
    def do_work(self):
        # Calls 3 methods from other classes (within limit of 5)
        self.service_a.method_a1()
        self.service_a.method_a2()
        self.service_b.method_b1()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should not find TC003 violations (but might find TC001)
        captured = capsys.readouterr()
        # Check that if there are violations, they're not TC003
        if "violations" in captured.out.lower():
            assert "TC003" not in captured.out or exit_code != 2
    finally:
        sys.argv = old_argv


def test_excessive_interaction_multiple_classes(tmp_path: Path, capsys):
    """Test detection when multiple classes have excessive interactions."""
    project_dir = tmp_path / "interaction_project3"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_inter_class_calls = 2
""")

    # Create a file with multiple violating classes
    (project_dir / "multiple_violations.py").write_text("""
class ServiceA:
    def method_a(self):
        pass

class ServiceB:
    def method_b(self):
        pass

class ServiceC:
    def method_c(self):
        pass

class Client1:
    def __init__(self):
        self.a = ServiceA()
        self.b = ServiceB()
        self.c = ServiceC()
    
    def work(self):
        # Calls 3 methods (exceeds max of 2)
        self.a.method_a()
        self.b.method_b()
        self.c.method_c()

class Client2:
    def __init__(self):
        self.a = ServiceA()
        self.b = ServiceB()
        self.c = ServiceC()
    
    def work(self):
        # Also calls 3 methods (exceeds max of 2)
        self.a.method_a()
        self.b.method_b()
        self.c.method_c()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        assert exit_code == 2
        captured = capsys.readouterr()
        # Should find TC003 violations
        tc003_count = captured.out.count("TC003")
        assert tc003_count >= 2, f"Expected at least 2 TC003 violations, found {tc003_count}"
    finally:
        sys.argv = old_argv


def test_excessive_interaction_same_class_calls_ignored(tmp_path: Path, capsys):
    """Test that calls within the same class don't count toward the limit."""
    project_dir = tmp_path / "interaction_project4"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_inter_class_calls = 2
""")

    # Create a file where a class calls its own methods many times
    (project_dir / "self_calls.py").write_text("""
class ServiceA:
    def method_a(self):
        pass

class Worker:
    def __init__(self):
        self.service = ServiceA()
    
    def helper1(self):
        pass
    
    def helper2(self):
        pass
    
    def helper3(self):
        pass
    
    def do_work(self):
        # Many calls to own methods (should not count)
        self.helper1()
        self.helper2()
        self.helper3()
        # Only 1 call to external class (within limit)
        self.service.method_a()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        captured = capsys.readouterr()
        # Should not find TC003 violations
        if "violations" in captured.out.lower():
            assert "TC003" not in captured.out or exit_code != 2
    finally:
        sys.argv = old_argv


def test_excessive_interaction_default_config(tmp_path: Path, capsys):
    """Test that default max_inter_class_calls (10) is used when not configured."""
    project_dir = tmp_path / "interaction_project5"
    project_dir.mkdir()

    # No pyproject.toml - should use default max_inter_class_calls = 10

    # Create a file with 8 inter-class calls (should be OK with default)
    (project_dir / "default_config.py").write_text("""
class S1:
    def m1(self): pass

class S2:
    def m2(self): pass

class S3:
    def m3(self): pass

class S4:
    def m4(self): pass

class Client:
    def __init__(self):
        self.s1 = S1()
        self.s2 = S2()
        self.s3 = S3()
        self.s4 = S4()
    
    def work(self):
        # 8 calls to external classes (within default limit of 10)
        self.s1.m1()
        self.s1.m1()
        self.s2.m2()
        self.s2.m2()
        self.s3.m3()
        self.s3.m3()
        self.s4.m4()
        self.s4.m4()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should not find TC003 violations with default config
        captured = capsys.readouterr()
        if "violations" in captured.out.lower():
            assert "TC003" not in captured.out or exit_code != 2
    finally:
        sys.argv = old_argv


def test_excessive_interaction_counts_unique_methods(tmp_path: Path, capsys):
    """Test that calling the same method multiple times only counts once."""
    project_dir = tmp_path / "interaction_project6"
    project_dir.mkdir()

    # Create pyproject.toml
    pyproject_toml = project_dir / "pyproject.toml"
    pyproject_toml.write_text("""
[tool.vera_syntaxis.coupling]
max_inter_class_calls = 2
""")

    # Create a file where same method is called multiple times
    (project_dir / "repeated_calls.py").write_text("""
class ServiceA:
    def method_a(self):
        pass

class Client:
    def __init__(self):
        self.service = ServiceA()
    
    def work(self):
        # Same method called 5 times, but counts as 1 unique call
        self.service.method_a()
        self.service.method_a()
        self.service.method_a()
        self.service.method_a()
        self.service.method_a()
""")

    # Run the analysis
    old_argv = sys.argv
    try:
        sys.argv = ["vera-syntaxis", "analyze", str(project_dir)]
        exit_code = main()
        
        # Should not find TC003 violations (only 1 unique method called)
        captured = capsys.readouterr()
        if "violations" in captured.out.lower():
            assert "TC003" not in captured.out or exit_code != 2
    finally:
        sys.argv = old_argv

"""Integration tests for Phase 1 functionality."""

import pytest
from pathlib import Path
from vera_syntaxis.file_discovery import discover_python_files
from vera_syntaxis.parser import ASTParser
from vera_syntaxis.visitor import BaseVisitor, MultiPassVisitor
import ast


def test_end_to_end_file_discovery_and_parsing(sample_project: Path):
    """Test complete workflow: discover files and parse them."""
    # Step 1: Discover files
    python_files = discover_python_files(sample_project)
    assert len(python_files) > 0
    
    # Step 2: Parse all discovered files
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Step 3: Verify results
    assert len(parsed_files) > 0
    assert all(pf.ast_root is not None for pf in parsed_files.values())
    
    # Step 4: Check that we can get import maps
    for file_path in parsed_files:
        import_map = parser.get_import_map(file_path)
        assert isinstance(import_map, dict)


def test_end_to_end_with_visitor(sample_project: Path):
    """Test complete workflow including AST visiting."""
    
    class ClassCounter(BaseVisitor):
        """Visitor that counts classes."""
        def __init__(self, file_path: Path):
            super().__init__(file_path)
            self.class_count = 0
        
        def visit_ClassDef(self, node: ast.ClassDef):
            self.class_count += 1
            return super().visit_ClassDef(node)
    
    # Discover and parse
    python_files = discover_python_files(sample_project)
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Visit all parsed files
    total_classes = 0
    for file_path, parsed_file in parsed_files.items():
        visitor = ClassCounter(file_path)
        visitor.visit(parsed_file.ast_root)
        total_classes += visitor.class_count
    
    # Sample project has at least one class (User)
    assert total_classes >= 1


def test_multi_pass_analysis_workflow(sample_project: Path):
    """Test multi-pass analysis workflow."""
    
    class FirstPass(BaseVisitor):
        """First pass: collect class names."""
        def __init__(self, file_path: Path):
            super().__init__(file_path)
            self.classes = []
        
        def visit_ClassDef(self, node: ast.ClassDef):
            self.classes.append(node.name)
            return super().visit_ClassDef(node)
    
    class SecondPass(BaseVisitor):
        """Second pass: collect method names."""
        def __init__(self, file_path: Path):
            super().__init__(file_path)
            self.methods = []
        
        def visit_FunctionDef(self, node: ast.FunctionDef):
            self.methods.append(node.name)
            return super().visit_FunctionDef(node)
    
    # Discover and parse
    python_files = discover_python_files(sample_project)
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Run multi-pass analysis on each file
    for file_path, parsed_file in parsed_files.items():
        multi_pass = MultiPassVisitor()
        
        first = FirstPass(file_path)
        second = SecondPass(file_path)
        
        multi_pass.add_pass(first)
        multi_pass.add_pass(second)
        
        results = multi_pass.run_passes(parsed_file.ast_root)
        
        assert 'FirstPass_1' in results
        assert 'SecondPass_2' in results


def test_parse_real_vera_syntaxis_code():
    """Test parsing the Vera Syntaxis codebase itself."""
    # Get the path to vera_syntaxis package
    import vera_syntaxis
    package_path = Path(vera_syntaxis.__file__).parent
    
    # Discover files in the package
    python_files = discover_python_files(package_path)
    
    # Should find at least: __init__.py, file_discovery.py, parser.py, visitor.py, cli.py
    assert len(python_files) >= 5
    
    # Parse all files
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # All files should parse successfully (no syntax errors in our own code!)
    assert len(parser.parse_errors) == 0
    assert len(parsed_files) == len(python_files)


def test_import_resolution_across_files(temp_project_dir: Path):
    """Test that imports can be tracked across multiple files."""
    # Create a multi-file project
    (temp_project_dir / "models").mkdir()
    
    # models/user.py
    (temp_project_dir / "models" / "user.py").write_text("""
class User:
    def __init__(self, name: str):
        self.name = name
""", encoding='utf-8')
    
    # main.py imports from models
    (temp_project_dir / "main.py").write_text("""
from models.user import User

def create_user():
    return User("Alice")
""", encoding='utf-8')
    
    # Discover and parse
    python_files = discover_python_files(temp_project_dir)
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Check import map for main.py
    main_py = temp_project_dir / "main.py"
    import_map = parser.get_import_map(main_py)
    
    assert 'User' in import_map
    assert import_map['User'] == 'models.user.User'


def test_error_handling_with_mixed_valid_invalid_files(temp_project_dir: Path):
    """Test that parser handles mix of valid and invalid files gracefully."""
    # Create valid file
    (temp_project_dir / "valid.py").write_text("""
def valid_function():
    return True
""", encoding='utf-8')
    
    # Create invalid file
    (temp_project_dir / "invalid.py").write_text("""
def invalid_function(
    # Missing closing paren and body
""", encoding='utf-8')
    
    # Discover and parse
    python_files = discover_python_files(temp_project_dir)
    parser = ASTParser()
    parsed_files = parser.parse_files(python_files)
    
    # Should have one success and one error
    assert len(parsed_files) == 1
    assert len(parser.parse_errors) == 1
    
    # Valid file should be in parsed_files
    valid_path = temp_project_dir / "valid.py"
    assert valid_path in parsed_files
    
    # Invalid file should be in errors
    assert any(e.file_path.name == "invalid.py" for e in parser.parse_errors)


def test_cli_parse_command_integration(sample_project: Path, capsys):
    """Test the CLI parse command end-to-end."""
    from vera_syntaxis.cli import cmd_parse
    import argparse
    
    # Create args namespace
    args = argparse.Namespace(
        project_path=sample_project,
        dump_ast=False,
        verbose=False
    )
    
    # Run parse command
    exit_code = cmd_parse(args)
    
    # Should succeed
    assert exit_code == 0
    
    # Check output
    captured = capsys.readouterr()
    assert "Parse Results" in captured.out
    assert "Successfully parsed:" in captured.out


def test_cli_analyze_command_integration(sample_project: Path, capsys):
    """Test the CLI analyze command end-to-end including symbol table building."""
    from vera_syntaxis.cli import cmd_analyze
    import argparse
    
    # Create args namespace
    args = argparse.Namespace(
        project_path=sample_project,
        config=None,
        verbose=False
    )
    
    # Run analyze command - this should build symbol table correctly
    exit_code = cmd_analyze(args)
    
    # Should succeed (0 = no violations, 2 = violations found, both are success)
    assert exit_code in (0, 2)
    
    # Check output
    captured = capsys.readouterr()
    # Should complete without errors about missing arguments
    assert "missing" not in captured.out.lower()
    assert "positional arguments" not in captured.out.lower()

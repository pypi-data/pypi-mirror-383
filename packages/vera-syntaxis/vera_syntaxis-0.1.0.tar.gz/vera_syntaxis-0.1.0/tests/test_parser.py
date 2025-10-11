"""Tests for AST parser module."""

import pytest
import ast
from pathlib import Path
from vera_syntaxis.parser import ASTParser, ParsedFile, ParseError


def test_parse_simple_file(sample_python_file: Path):
    """Test parsing a simple Python file."""
    parser = ASTParser()
    parsed = parser.parse_file(sample_python_file)
    
    assert parsed is not None
    assert isinstance(parsed, ParsedFile)
    assert parsed.file_path == sample_python_file
    assert isinstance(parsed.ast_root, ast.Module)
    assert len(parsed.imports) > 0


def test_parse_file_extracts_imports(sample_python_file: Path):
    """Test that imports are correctly extracted."""
    parser = ASTParser()
    parsed = parser.parse_file(sample_python_file)
    
    assert parsed is not None
    # Sample file has: import os, from typing import List
    assert len(parsed.imports) == 2
    
    # Check import types
    import_types = [type(imp) for imp in parsed.imports]
    assert ast.Import in import_types
    assert ast.ImportFrom in import_types


def test_parse_file_with_syntax_error(temp_project_dir: Path):
    """Test parsing a file with syntax errors."""
    bad_file = temp_project_dir / "bad.py"
    bad_file.write_text("def bad_function(\n    # Missing closing paren", encoding='utf-8')
    
    parser = ASTParser()
    parsed = parser.parse_file(bad_file)
    
    assert parsed is None
    assert len(parser.parse_errors) == 1
    
    error = parser.parse_errors[0]
    assert isinstance(error, ParseError)
    assert error.file_path == bad_file
    assert error.error_type == "SyntaxError"
    assert error.line_number is not None


def test_parse_multiple_files(sample_project: Path):
    """Test parsing multiple files at once."""
    from vera_syntaxis.file_discovery import discover_python_files
    
    files = discover_python_files(sample_project)
    parser = ASTParser()
    parsed_files = parser.parse_files(files)
    
    assert len(parsed_files) > 0
    assert all(isinstance(pf, ParsedFile) for pf in parsed_files.values())


def test_get_import_map_simple_import(temp_project_dir: Path):
    """Test building import map for simple imports."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
import os
import sys as system
from typing import List, Dict
from pathlib import Path as P
""", encoding='utf-8')
    
    parser = ASTParser()
    parser.parse_file(test_file)
    import_map = parser.get_import_map(test_file)
    
    assert import_map['os'] == 'os'
    assert import_map['system'] == 'sys'
    assert import_map['List'] == 'typing.List'
    assert import_map['Dict'] == 'typing.Dict'
    assert import_map['P'] == 'pathlib.Path'


def test_get_import_map_from_import(temp_project_dir: Path):
    """Test building import map for from imports."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
from collections import defaultdict
from typing import List as ListType
""", encoding='utf-8')
    
    parser = ASTParser()
    parser.parse_file(test_file)
    import_map = parser.get_import_map(test_file)
    
    assert import_map['defaultdict'] == 'collections.defaultdict'
    assert import_map['ListType'] == 'typing.List'


def test_get_import_map_unparsed_file(temp_project_dir: Path):
    """Test getting import map for a file that hasn't been parsed."""
    parser = ASTParser()
    nonexistent = temp_project_dir / "nonexistent.py"
    import_map = parser.get_import_map(nonexistent)
    
    assert import_map == {}


def test_parser_caches_results(sample_python_file: Path):
    """Test that parser caches parsed files."""
    parser = ASTParser()
    
    # Parse once
    parsed1 = parser.parse_file(sample_python_file)
    assert sample_python_file in parser.parsed_files
    
    # Check cache
    cached = parser.parsed_files[sample_python_file]
    assert cached == parsed1


def test_clear_cache(sample_python_file: Path):
    """Test clearing the parser cache."""
    parser = ASTParser()
    parser.parse_file(sample_python_file)
    
    assert len(parser.parsed_files) > 0
    
    parser.clear_cache()
    
    assert len(parser.parsed_files) == 0
    assert len(parser.parse_errors) == 0


def test_parse_file_with_unicode(temp_project_dir: Path):
    """Test parsing a file with Unicode characters."""
    unicode_file = temp_project_dir / "unicode.py"
    unicode_file.write_text("""
# -*- coding: utf-8 -*-
def greet():
    return "Hello, 世界! 🌍"
""", encoding='utf-8')
    
    parser = ASTParser()
    parsed = parser.parse_file(unicode_file)
    
    assert parsed is not None
    assert parsed.encoding == 'utf-8'


def test_parse_empty_file(temp_project_dir: Path):
    """Test parsing an empty Python file."""
    empty_file = temp_project_dir / "empty.py"
    empty_file.write_text("", encoding='utf-8')
    
    parser = ASTParser()
    parsed = parser.parse_file(empty_file)
    
    assert parsed is not None
    assert isinstance(parsed.ast_root, ast.Module)
    assert len(parsed.imports) == 0


def test_parse_files_reports_statistics(sample_project: Path):
    """Test that parse_files provides accurate statistics."""
    from vera_syntaxis.file_discovery import discover_python_files
    
    # Add a file with syntax error
    bad_file = sample_project / "bad.py"
    bad_file.write_text("def bad(:\n    pass", encoding='utf-8')
    
    files = discover_python_files(sample_project)
    parser = ASTParser()
    parsed_files = parser.parse_files(files)
    
    # Should have some successful parses and one error
    assert len(parsed_files) > 0
    assert len(parser.parse_errors) == 1

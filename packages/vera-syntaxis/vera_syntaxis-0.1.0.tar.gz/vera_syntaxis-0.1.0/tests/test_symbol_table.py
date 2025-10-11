"""Tests for the symbol table module."""

import pytest
import ast
from pathlib import Path
from vera_syntaxis.symbol_table import (
    SymbolTable, SymbolTableBuilder, ClassSymbol, MethodSymbol, VariableSymbol
)

@pytest.fixture
def symbol_table() -> SymbolTable:
    return SymbolTable()

@pytest.fixture
def sample_code() -> str:
    return """
import os
from typing import List

class MyClass(BaseClass):
    class_attr: int = 10

    def __init__(self, value: int):
        self.instance_attr = value

    def my_method(self, x: int) -> int:
        local_var = x + self.instance_attr
        return local_var

    async def my_async_method(self) -> None:
        pass

    @staticmethod
    def static_method():
        pass

MODULE_VAR = "hello"
"""

@pytest.fixture
def parsed_ast(sample_code: str) -> ast.Module:
    return ast.parse(sample_code)

def test_symbol_table_builder(parsed_ast: ast.Module, symbol_table: SymbolTable, temp_project_dir: Path):
    file_path = temp_project_dir / "test.py"
    builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
    builder.visit(parsed_ast)

    # Check class symbol
    class_symbol = symbol_table.get_symbol("test.MyClass")
    assert isinstance(class_symbol, ClassSymbol)
    assert class_symbol.name == "test.MyClass"
    assert "BaseClass" in class_symbol.base_classes
    assert len(class_symbol.methods) == 4
    assert len(class_symbol.attributes) == 2 # class_attr and instance_attr

    # Check method symbol
    method_symbol = symbol_table.get_symbol("test.MyClass.my_method")
    assert isinstance(method_symbol, MethodSymbol)
    assert method_symbol.name == "test.MyClass.my_method"
    assert method_symbol.return_type == "int"
    assert method_symbol.arg_types["x"] == "int"

    # Check instance attribute defined in __init__
    inst_attr_symbol = symbol_table.get_symbol("test.MyClass.instance_attr")
    assert isinstance(inst_attr_symbol, VariableSymbol)
    assert inst_attr_symbol.type_hint == "int"

    # Check module-level variable
    module_var = symbol_table.get_symbol("test.MODULE_VAR")
    assert isinstance(module_var, VariableSymbol)

def test_qualified_name_generation(parsed_ast: ast.Module, symbol_table: SymbolTable, temp_project_dir: Path):
    file_path = temp_project_dir / "test.py"
    builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
    builder.visit(parsed_ast)

    method_symbol = symbol_table.get_symbol("test.MyClass.my_method")
    assert method_symbol.qualified_name == "test.MyClass.my_method"

    class_symbol = symbol_table.get_symbol("test.MyClass")
    assert class_symbol.qualified_name == "test.MyClass"

    module_var = symbol_table.get_symbol("test.MODULE_VAR")
    assert module_var.qualified_name == "test.MODULE_VAR"

def test_add_and_get_symbol(symbol_table: SymbolTable, temp_project_dir: Path):
    file_path = temp_project_dir / "test.py"
    symbol = VariableSymbol(name="my_module.my_var", file_path=file_path, line_number=1)
    symbol_table.add_symbol(symbol)

    retrieved = symbol_table.get_symbol("my_module.my_var")
    assert retrieved == symbol

def test_duplicate_symbol_warning(symbol_table: SymbolTable, temp_project_dir: Path, caplog):
    file_path = temp_project_dir / "test.py"
    symbol1 = VariableSymbol(name="my_module.my_var", file_path=file_path, line_number=1)
    symbol2 = VariableSymbol(name="my_module.my_var", file_path=file_path, line_number=2)

    symbol_table.add_symbol(symbol1)
    with caplog.at_level('WARNING'):
        symbol_table.add_symbol(symbol2)
    
    assert "Duplicate symbol found" in caplog.text
    assert symbol_table.get_symbol("my_module.my_var") == symbol2

def test_type_inference_from_assignment(symbol_table: SymbolTable, temp_project_dir: Path):
    """Test that the builder infers type from 'var = Class()' assignment."""
    file_path = temp_project_dir / "test.py"
    code = """
class MyService:
    pass

service_instance = MyService()
"""
    parsed_ast = ast.parse(code)
    builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
    builder.visit(parsed_ast)

    symbol = symbol_table.get_symbol("test.service_instance")
    assert isinstance(symbol, VariableSymbol)
    assert symbol.type_hint == "MyService"



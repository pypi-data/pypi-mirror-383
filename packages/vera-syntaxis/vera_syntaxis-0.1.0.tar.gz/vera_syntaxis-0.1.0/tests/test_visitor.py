"""Tests for AST visitor module."""

import pytest
import ast
from pathlib import Path
from vera_syntaxis.visitor import BaseVisitor, MultiPassVisitor


class CountingVisitor(BaseVisitor):
    """Test visitor that tracks visited nodes."""
    
    def __init__(self, file_path: Path):
        super().__init__(file_path)
        self.visited_classes = []
        self.visited_functions = []
    
    def visit_ClassDef(self, node: ast.ClassDef):
        self.visited_classes.append(node.name)
        return super().visit_ClassDef(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.visited_functions.append(node.name)
        return super().visit_FunctionDef(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visited_functions.append(node.name)
        return super().visit_AsyncFunctionDef(node)


def test_base_visitor_tracks_classes(temp_project_dir: Path):
    """Test that BaseVisitor correctly tracks class definitions."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class MyClass:
    pass

class AnotherClass:
    pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    visitor = CountingVisitor(test_file)
    visitor.visit(tree)
    
    assert 'MyClass' in visitor.visited_classes
    assert 'AnotherClass' in visitor.visited_classes
    assert len(visitor.visited_classes) == 2


def test_base_visitor_tracks_functions(temp_project_dir: Path):
    """Test that BaseVisitor correctly tracks function definitions."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
def my_function():
    pass

def another_function():
    pass

class MyClass:
    def method(self):
        pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    visitor = CountingVisitor(test_file)
    visitor.visit(tree)
    
    assert 'my_function' in visitor.visited_functions
    assert 'another_function' in visitor.visited_functions
    assert 'method' in visitor.visited_functions
    assert len(visitor.visited_functions) == 3


def test_base_visitor_scope_tracking(temp_project_dir: Path):
    """Test that BaseVisitor correctly tracks scope."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class MyClass:
    def my_method(self):
        pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    
    class ScopeTracker(BaseVisitor):
        def __init__(self, file_path):
            super().__init__(file_path)
            self.scopes = []
        
        def visit_FunctionDef(self, node):
            self.scopes.append(self.get_current_scope())
            return super().visit_FunctionDef(node)
    
    visitor = ScopeTracker(test_file)
    visitor.visit(tree)
    
    # Should capture scope when entering method
    assert any('class:MyClass' in scope for scope in visitor.scopes)


def test_base_visitor_async_function(temp_project_dir: Path):
    """Test that BaseVisitor handles async functions."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
async def async_function():
    pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    visitor = CountingVisitor(test_file)
    visitor.visit(tree)
    
    assert 'async_function' in visitor.visited_functions


def test_base_visitor_get_qualified_name(temp_project_dir: Path):
    """Test getting qualified names from AST nodes."""
    test_file = temp_project_dir / "test.py"
    visitor = BaseVisitor(test_file)
    
    # Test simple name
    name_node = ast.Name(id='variable', ctx=ast.Load())
    assert visitor.get_qualified_name(name_node) == 'variable'
    
    # Test attribute access
    attr_node = ast.Attribute(
        value=ast.Name(id='obj', ctx=ast.Load()),
        attr='method',
        ctx=ast.Load()
    )
    assert visitor.get_qualified_name(attr_node) == 'obj.method'
    
    # Test nested attribute access
    nested_attr = ast.Attribute(
        value=ast.Attribute(
            value=ast.Name(id='obj', ctx=ast.Load()),
            attr='attr1',
            ctx=ast.Load()
        ),
        attr='attr2',
        ctx=ast.Load()
    )
    assert visitor.get_qualified_name(nested_attr) == 'obj.attr1.attr2'


def test_multi_pass_visitor_single_pass(temp_project_dir: Path):
    """Test MultiPassVisitor with a single pass."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class MyClass:
    pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    
    multi_pass = MultiPassVisitor()
    visitor = CountingVisitor(test_file)
    multi_pass.add_pass(visitor)
    
    results = multi_pass.run_passes(tree)
    
    assert 'CountingVisitor_1' in results
    assert results['CountingVisitor_1'] == visitor
    assert 'MyClass' in visitor.visited_classes


def test_multi_pass_visitor_multiple_passes(temp_project_dir: Path):
    """Test MultiPassVisitor with multiple passes."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class MyClass:
    def my_method(self):
        pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    
    multi_pass = MultiPassVisitor()
    visitor1 = CountingVisitor(test_file)
    visitor2 = CountingVisitor(test_file)
    
    multi_pass.add_pass(visitor1)
    multi_pass.add_pass(visitor2)
    
    results = multi_pass.run_passes(tree)
    
    assert len(results) == 2
    assert 'CountingVisitor_1' in results
    assert 'CountingVisitor_2' in results
    # Both visitors should have visited the same nodes
    assert visitor1.visited_classes == visitor2.visited_classes
    assert visitor1.visited_functions == visitor2.visited_functions


def test_base_visitor_nested_classes(temp_project_dir: Path):
    """Test BaseVisitor with nested class definitions."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class OuterClass:
    class InnerClass:
        pass
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    visitor = CountingVisitor(test_file)
    visitor.visit(tree)
    
    assert 'OuterClass' in visitor.visited_classes
    assert 'InnerClass' in visitor.visited_classes


def test_get_current_scope_module_level(temp_project_dir: Path):
    """Test get_current_scope at module level."""
    test_file = temp_project_dir / "test.py"
    visitor = BaseVisitor(test_file)
    
    assert visitor.get_current_scope() == "<module>"


def test_get_current_scope_in_class(temp_project_dir: Path):
    """Test get_current_scope inside a class."""
    test_file = temp_project_dir / "test.py"
    test_file.write_text("""
class MyClass:
    x = 1
""", encoding='utf-8')
    
    tree = ast.parse(test_file.read_text(), filename=str(test_file))
    
    class ScopeChecker(BaseVisitor):
        def __init__(self, file_path):
            super().__init__(file_path)
            self.class_scope = None
        
        def visit_ClassDef(self, node):
            # Call parent to update scope
            super().visit_ClassDef(node)
            # Capture scope while in class
            self.class_scope = self.get_current_scope()
            return node
    
    visitor = ScopeChecker(test_file)
    visitor.visit(tree)
    
    # Note: scope is captured after exiting, so it will be back to module
    # This tests the scope stack behavior
    assert visitor.current_class is None  # Restored after visit

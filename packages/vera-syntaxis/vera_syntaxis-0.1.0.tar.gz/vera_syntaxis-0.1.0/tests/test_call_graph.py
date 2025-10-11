"""Tests for the call graph module."""

import pytest
import ast
import networkx as nx
from pathlib import Path
from vera_syntaxis.symbol_table import SymbolTable, SymbolTableBuilder
from vera_syntaxis.call_graph import CallGraphBuilder, build_call_graph
from vera_syntaxis.parser import ASTParser

@pytest.fixture
def sample_call_code() -> str:
    return """
class ServiceA:
    def method_a(self):
        pass

class ServiceB:
    def __init__(self):
        self.service_a = ServiceA()

    def method_b(self):
        self.service_a.method_a()

    def method_c(self):
        self.method_b()
"""

@pytest.fixture
def call_graph_components(sample_call_code: str, temp_project_dir: Path) -> dict:
    file_path = temp_project_dir / "test.py"
    file_path.write_text(sample_call_code)

    parser = ASTParser(temp_project_dir)
    parsed_file = parser.parse_file(file_path)

    symbol_table = SymbolTable()
    st_builder = SymbolTableBuilder(file_path, temp_project_dir, symbol_table)
    st_builder.visit(parsed_file.ast_root)

    return {
        "parser": parser,
        "symbol_table": symbol_table,
        "parsed_files": {file_path: parsed_file}
    }

def test_build_call_graph(call_graph_components: dict):
    parser = call_graph_components["parser"]
    symbol_table = call_graph_components["symbol_table"]
    parsed_files = call_graph_components["parsed_files"]

    graph = build_call_graph(parser, symbol_table, parsed_files)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() > 0
    assert graph.number_of_edges() > 0

    # Check for specific edge: method_c -> method_b
    assert graph.has_edge("test.ServiceB.method_c", "test.ServiceB.method_b")

    # Check for specific edge: method_b -> ServiceA.method_a
    assert graph.has_edge("test.ServiceB.method_b", "test.ServiceA.method_a")

def test_call_graph_builder_visitor(call_graph_components: dict):
    symbol_table = call_graph_components["symbol_table"]
    parsed_file = list(call_graph_components["parsed_files"].values())[0]
    file_path = parsed_file.file_path

    graph = nx.DiGraph()
    parser = call_graph_components["parser"]
    builder = CallGraphBuilder(file_path, parser, symbol_table, graph)
    builder.visit(parsed_file.ast_root)

    # Check that the graph was populated
    assert graph.number_of_edges() > 0


"""Tests for the configuration loading module."""

import pytest
from pathlib import Path
from vera_syntaxis.config import load_config, VeraSyntaxisConfig

@pytest.fixture
def project_with_config(temp_project_dir: Path) -> Path:
    config_content = """
[tool.vera_syntaxis]
module_filter = ["my_app.*"]

[tool.vera_syntaxis.coupling]
max_demeter_chain = 3

[tool.vera_syntaxis.mvbc]
model_paths = ["app/models"]
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)
    return temp_project_dir

def test_load_config_from_file(project_with_config: Path):
    """Test that configuration is correctly loaded from a pyproject.toml file."""
    config = load_config(project_with_config)

    assert config.module_filter == ["my_app.*"]
    assert config.coupling.max_demeter_chain == 3
    assert config.mvbc.model_paths == ["app/models"]
    # Check that a default value is present
    assert config.coupling.max_inter_class_calls == 10

def test_load_default_config(temp_project_dir: Path):
    """Test that a default configuration is returned when no file is present."""
    config = load_config(temp_project_dir)

    assert isinstance(config, VeraSyntaxisConfig)
    # Check a default value
    assert config.coupling.max_demeter_chain == 5

def test_load_config_invalid_toml(temp_project_dir: Path, caplog):
    """Test fallback to default config when pyproject.toml is invalid."""
    (temp_project_dir / "pyproject.toml").write_text("[tool.vera_syntaxis] oops this is not valid")

    config = load_config(temp_project_dir)

    assert "Error decoding pyproject.toml" in caplog.text
    assert isinstance(config, VeraSyntaxisConfig)
    assert config.coupling.max_demeter_chain == 5 # Default value

def test_load_config_invalid_data(temp_project_dir: Path, caplog):
    """Test fallback to default config when config data is invalid."""
    config_content = """
[tool.vera_syntaxis.coupling]
max_demeter_chain = "not-an-int"
"""
    (temp_project_dir / "pyproject.toml").write_text(config_content)

    config = load_config(temp_project_dir)

    assert "Invalid configuration" in caplog.text
    assert isinstance(config, VeraSyntaxisConfig)
    assert config.coupling.max_demeter_chain == 5 # Default value

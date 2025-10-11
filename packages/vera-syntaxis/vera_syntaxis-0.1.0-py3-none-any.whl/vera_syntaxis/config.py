"""Configuration management for Vera Syntaxis using Pydantic."""

import logging
from pathlib import Path
from typing import List, Optional, Dict

import tomli
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

class CouplingConfig(BaseModel):
    """Configuration for the Tight Coupling linter."""
    max_inter_class_calls: int = Field(10, description="Maximum allowed calls from one class to another.")
    max_demeter_chain: int = Field(5, description="Maximum allowed length for a method call chain (Law of Demeter).")

class MVBCConfig(BaseModel):
    """Configuration for the MVBC (Model-View-Business-Controller) linter."""
    model_paths: List[str] = Field(default_factory=list, description="Glob patterns for Model layer files.")
    view_paths: List[str] = Field(default_factory=list, description="Glob patterns for View layer files.")
    business_paths: List[str] = Field(default_factory=list, description="Glob patterns for Business layer files.")
    controller_paths: List[str] = Field(default_factory=list, description="Glob patterns for Controller layer files.")


class CircularDependencyConfig(BaseModel):
    """Configuration for the Circular Dependency linter."""
    allow_self_cycles: bool = Field(False, description="Allow methods to call themselves (recursion).")
    max_cycle_length: int = Field(10, description="Maximum cycle length to report (prevents huge cycles).")


class GodObjectConfig(BaseModel):
    """Configuration for the God Object linter."""
    max_methods: int = Field(20, description="Maximum number of methods allowed in a class.")
    max_attributes: int = Field(15, description="Maximum number of attributes allowed in a class.")
    max_lines: int = Field(300, description="Maximum number of lines allowed in a class.")


class FeatureEnvyConfig(BaseModel):
    """Configuration for the Feature Envy linter."""
    envy_threshold: float = Field(0.5, description="Ratio of external to internal access that triggers feature envy (0.0-1.0).")
    min_accesses: int = Field(3, description="Minimum total accesses before checking for feature envy.")


class DataClumpConfig(BaseModel):
    """Configuration for the Data Clump linter."""
    min_clump_size: int = Field(3, description="Minimum number of parameters that appear together to be considered a clump.")
    min_occurrences: int = Field(2, description="Minimum number of methods with the same parameter group to trigger.")


class VeraSyntaxisConfig(BaseModel):
    """Main configuration model for Vera Syntaxis."""
    module_filter: List[str] = Field(['*'], description="Glob patterns to include modules for analysis.")
    coupling: CouplingConfig = Field(default_factory=CouplingConfig)
    mvbc: MVBCConfig = Field(default_factory=MVBCConfig)
    circular: CircularDependencyConfig = Field(default_factory=CircularDependencyConfig)
    god_object: GodObjectConfig = Field(default_factory=GodObjectConfig)
    feature_envy: FeatureEnvyConfig = Field(default_factory=FeatureEnvyConfig)
    data_clump: DataClumpConfig = Field(default_factory=DataClumpConfig)

def load_config(project_path: Path) -> VeraSyntaxisConfig:
    """
    Load Vera Syntaxis configuration from a pyproject.toml file.

    If no configuration is found, returns a default configuration.

    Args:
        project_path: The root path of the project to analyze.

    Returns:
        A validated VeraSyntaxisConfig instance.
    """
    pyproject_path = project_path / "pyproject.toml"

    if not pyproject_path.is_file():
        logger.warning("No pyproject.toml found. Using default configuration.")
        return VeraSyntaxisConfig()

    try:
        with open(pyproject_path, "rb") as f:
            toml_data = tomli.load(f)
    except tomli.TOMLDecodeError as e:
        logger.error(f"Error decoding pyproject.toml: {e}")
        return VeraSyntaxisConfig()

    config_data = toml_data.get("tool", {}).get("vera_syntaxis", {})

    if not config_data:
        logger.info("No [tool.vera_syntaxis] section in pyproject.toml. Using default configuration.")
        return VeraSyntaxisConfig()

    try:
        return VeraSyntaxisConfig.model_validate(config_data)
    except Exception as e:
        logger.error(f"Invalid configuration in pyproject.toml: {e}")
        logger.warning("Falling back to default configuration.")
        return VeraSyntaxisConfig()

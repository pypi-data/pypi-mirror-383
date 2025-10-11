"""Vera Syntaxis GUI - Graphical user interface for architectural linting.

This package provides a modern GUI application for running architectural analysis
and viewing results with syntax highlighting and interactive reports.
"""

__version__ = "0.1.0"

# GUI entry point
from vera_syntaxis.gui.launch_gui import main as launch_gui

__all__ = ['launch_gui']

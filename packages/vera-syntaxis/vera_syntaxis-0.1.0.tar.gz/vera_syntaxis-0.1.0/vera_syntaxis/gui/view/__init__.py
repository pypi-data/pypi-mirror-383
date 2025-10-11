"""View layer for Vera Syntaxis GUI."""

from vera_syntaxis.gui.view.main_window import MainWindow
from vera_syntaxis.gui.view.menu_bar import MenuBar
from vera_syntaxis.gui.view.status_bar import StatusBar
from vera_syntaxis.gui.view.toolbar import Toolbar
from vera_syntaxis.gui.view.report_tabs import ReportTabs
from vera_syntaxis.gui.view.progress_dialog import ProgressDialog
from vera_syntaxis.gui.view.text_highlighter import TextHighlighter
from vera_syntaxis.gui.view.config_editor import ConfigEditorDialog

__all__ = [
    'MainWindow',
    'MenuBar', 
    'StatusBar',
    'Toolbar',
    'ReportTabs',
    'ProgressDialog',
    'TextHighlighter',
    'ConfigEditorDialog'
]

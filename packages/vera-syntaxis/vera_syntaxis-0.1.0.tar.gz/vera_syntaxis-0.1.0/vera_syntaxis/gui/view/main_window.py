"""Main Window for Vera Syntaxis GUI."""

import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

from vera_syntaxis.gui.view.menu_bar import MenuBar
from vera_syntaxis.gui.view.status_bar import StatusBar
from vera_syntaxis.gui.view.report_tabs import ReportTabs
from vera_syntaxis.gui.view.toolbar import Toolbar


class MainWindow:
    """Main application window (View)."""
    
    def __init__(self, root: tb.Window):
        """
        Initialize the main window.
        
        Args:
            root: The root ttkbootstrap window
        """
        self.root = root
        self.root.title("Vera Syntaxis - Architectural Linter")
        self.root.geometry("1200x800")
        
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        
        # Initialize components
        self.menu_bar = MenuBar(self.root)
        self.toolbar = Toolbar(self.main_container)
        self.report_tabs = ReportTabs(self.main_container)
        self.status_bar = StatusBar(self.root)
        
        # Pack components
        self.toolbar.frame.pack(fill=X, padx=5, pady=5)
        self.report_tabs.notebook.pack(fill=BOTH, expand=YES, padx=5, pady=5)
        self.status_bar.frame.pack(side=BOTTOM, fill=X)
        
    def set_controller(self, controller):
        """
        Set the controller and bind callbacks.
        
        Args:
            controller: The app controller
        """
        # Bind menu actions
        self.menu_bar.set_open_folder_callback(controller.on_open_folder)
        self.menu_bar.set_analyze_callback(controller.on_analyze)
        self.menu_bar.set_save_report_callback(controller.on_save_report)
        self.menu_bar.set_exit_callback(controller.on_exit)
        self.menu_bar.set_copy_callback(controller.on_copy)
        self.menu_bar.set_config_callback(controller.on_edit_config)
        
        # Bind toolbar actions
        self.toolbar.set_open_callback(controller.on_open_folder)
        self.toolbar.set_analyze_callback(controller.on_analyze)
        self.toolbar.set_filter_callback(controller.on_filter_changed)
        
    def run(self):
        """Start the main event loop."""
        self.root.mainloop()

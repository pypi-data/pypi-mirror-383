"""Report Tabs component - displays linter results in tabs."""

import tkinter as tk
from tkinter import ttk, scrolledtext
from ttkbootstrap.constants import *

from vera_syntaxis.gui.view.text_highlighter import TextHighlighter


class ReportTabs:
    """Notebook with tabs for each linter's results."""
    
    # Tab configuration: (tab_name, rule_ids)
    TAB_CONFIG = [
        ("Summary", []),
        ("Pattern Opportunities", []),  # New tab for pattern detection
        ("Tight Coupling", ["TC001", "TC002", "TC003"]),
        ("MVBC", ["W2902"]),
        ("Circular Dependencies", ["CD001"]),
        ("God Objects", ["GO001"]),
        ("Feature Envy", ["FE001"]),
        ("Data Clumps", ["DC001"]),
    ]
    
    def __init__(self, parent):
        """
        Initialize the report tabs.
        
        Args:
            parent: Parent widget
        """
        self.notebook = ttk.Notebook(parent)
        self.tabs = {}
        self.text_widgets = {}
        
        self._create_tabs()
    
    def _create_tabs(self):
        """Create all tabs."""
        for tab_name, rule_ids in self.TAB_CONFIG:
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=tab_name)
            
            # Create scrolled text widget
            text_frame = ttk.Frame(tab_frame)
            text_frame.pack(fill=BOTH, expand=YES, padx=5, pady=5)
            
            text_widget = scrolledtext.ScrolledText(
                text_frame,
                wrap=tk.WORD,
                font=('Consolas', 10),
                state='disabled'
            )
            text_widget.pack(fill=BOTH, expand=YES)
            
            # Configure highlighting
            TextHighlighter.configure_text_widget(text_widget)
            
            # Add copy button
            btn_frame = ttk.Frame(tab_frame)
            btn_frame.pack(fill=X, padx=5, pady=5)
            
            copy_btn = ttk.Button(
                btn_frame,
                text="📋 Copy",
                command=lambda tw=text_widget: self._copy_text(tw),
                bootstyle=INFO
            )
            copy_btn.pack(side=RIGHT)
            
            self.tabs[tab_name] = tab_frame
            self.text_widgets[tab_name] = text_widget
    
    def _copy_text(self, text_widget):
        """
        Copy text from widget to clipboard.
        
        Args:
            text_widget: The text widget to copy from
        """
        try:
            text = text_widget.get('1.0', tk.END)
            text_widget.clipboard_clear()
            text_widget.clipboard_append(text)
        except:
            pass
    
    def update_tab(self, tab_name: str, content: str):
        """
        Update a tab's content with highlighted text.
        
        Args:
            tab_name: Name of the tab to update
            content: Text content to display
        """
        if tab_name not in self.text_widgets:
            return
        
        text_widget = self.text_widgets[tab_name]
        text_widget.config(state='normal')
        
        # Use highlighter to insert formatted text
        TextHighlighter.highlight_violation_report(text_widget, content)
        
        text_widget.config(state='disabled')
    
    def clear_all_tabs(self):
        """Clear content from all tabs."""
        for text_widget in self.text_widgets.values():
            text_widget.config(state='normal')
            text_widget.delete('1.0', tk.END)
            text_widget.config(state='disabled')
    
    def get_current_tab_name(self) -> str:
        """
        Get the name of the currently selected tab.
        
        Returns:
            Name of current tab
        """
        current_index = self.notebook.index(self.notebook.select())
        return self.TAB_CONFIG[current_index][0]

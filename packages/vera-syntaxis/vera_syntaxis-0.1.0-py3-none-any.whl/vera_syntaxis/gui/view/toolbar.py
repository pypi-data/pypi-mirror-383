"""Toolbar component."""

import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *


class Toolbar:
    """Toolbar with action buttons and filters."""
    
    def __init__(self, parent):
        """
        Initialize the toolbar.
        
        Args:
            parent: Parent widget
        """
        self.frame = ttk.Frame(parent)
        
        # Callbacks
        self._open_callback = None
        self._analyze_callback = None
        self._filter_callback = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create toolbar widgets."""
        # Open folder button
        self.open_btn = ttk.Button(
            self.frame,
            text="📁 Open Folder",
            command=self._on_open,
            bootstyle=PRIMARY
        )
        self.open_btn.pack(side=LEFT, padx=2)
        
        # Analyze button
        self.analyze_btn = ttk.Button(
            self.frame,
            text="▶ Analyze",
            command=self._on_analyze,
            bootstyle=SUCCESS,
            state='disabled'
        )
        self.analyze_btn.pack(side=LEFT, padx=2)
        
        # Separator
        ttk.Separator(self.frame, orient='vertical').pack(side=LEFT, fill=Y, padx=10, pady=5)
        
        # Filter controls
        ttk.Label(self.frame, text="Filter:").pack(side=LEFT, padx=5)
        
        self.filter_var = tk.StringVar(value="all")
        self.filter_combo = ttk.Combobox(
            self.frame,
            textvariable=self.filter_var,
            values=["all", "by file", "by severity"],
            state='readonly',
            width=15
        )
        self.filter_combo.pack(side=LEFT, padx=2)
        self.filter_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)
        
        self.filter_entry = ttk.Entry(self.frame, width=30)
        self.filter_entry.pack(side=LEFT, padx=2)
        self.filter_entry.bind('<Return>', self._on_filter_changed)
        self.filter_entry.insert(0, "Enter file path or rule ID...")
        self.filter_entry.bind('<FocusIn>', self._on_entry_focus_in)
        self.filter_entry.bind('<FocusOut>', self._on_entry_focus_out)
    
    def _on_open(self):
        if self._open_callback:
            self._open_callback()
    
    def _on_analyze(self):
        if self._analyze_callback:
            self._analyze_callback()
    
    def _on_filter_changed(self, event=None):
        if self._filter_callback:
            filter_type = self.filter_var.get()
            filter_text = self.filter_entry.get()
            if filter_text == "Enter file path or rule ID...":
                filter_text = ""
            self._filter_callback(filter_type, filter_text)
    
    def _on_entry_focus_in(self, event):
        if self.filter_entry.get() == "Enter file path or rule ID...":
            self.filter_entry.delete(0, 'end')
    
    def _on_entry_focus_out(self, event):
        if not self.filter_entry.get():
            self.filter_entry.insert(0, "Enter file path or rule ID...")
    
    def set_open_callback(self, callback):
        self._open_callback = callback
    
    def set_analyze_callback(self, callback):
        self._analyze_callback = callback
    
    def set_filter_callback(self, callback):
        self._filter_callback = callback
    
    def enable_analyze(self, enabled: bool = True):
        """Enable/disable analyze button."""
        self.analyze_btn.config(state='normal' if enabled else 'disabled')

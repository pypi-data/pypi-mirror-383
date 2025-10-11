"""Configuration Editor Dialog - full config editor for all linters."""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ttkbootstrap.constants import *
from pathlib import Path
from typing import Dict, Any


class ConfigEditorDialog:
    """Configuration editor dialog with settings for all linters."""
    
    # Configuration schema for all linters
    CONFIG_SCHEMA = {
        "Tight Coupling": {
            "section": "tight_coupling",
            "fields": [
                ("max_instantiations", "int", 5, "Maximum direct instantiations before reporting"),
                ("max_chain_length", "int", 2, "Maximum method chain length (Law of Demeter)"),
                ("max_interactions", "int", 10, "Maximum class interactions before reporting"),
            ]
        },
        "MVBC": {
            "section": "mvbc",
            "fields": [
                ("models_paths", "list", "models/**/*.py", "Glob patterns for model files"),
                ("views_paths", "list", "views/**/*.py", "Glob patterns for view files"),
                ("controllers_paths", "list", "controllers/**/*.py", "Glob patterns for controller files"),
            ]
        },
        "Circular Dependencies": {
            "section": "circular_dependencies",
            "fields": [
                ("enabled", "bool", True, "Enable circular dependency detection"),
            ]
        },
        "God Object": {
            "section": "god_object",
            "fields": [
                ("max_methods", "int", 20, "Maximum methods before flagging as God Object"),
                ("max_attributes", "int", 15, "Maximum attributes before flagging"),
                ("max_lines", "int", 300, "Maximum lines of code before flagging"),
            ]
        },
        "Feature Envy": {
            "section": "feature_envy",
            "fields": [
                ("envy_threshold", "float", 0.5, "Ratio of external to internal access (0.0-1.0)"),
                ("min_accesses", "int", 3, "Minimum attribute accesses before checking"),
            ]
        },
        "Data Clump": {
            "section": "data_clump",
            "fields": [
                ("min_clump_size", "int", 3, "Minimum parameters in a clump"),
                ("min_occurrences", "int", 2, "Minimum method occurrences for a clump"),
            ]
        },
    }
    
    def __init__(self, parent, current_config: Dict[str, Any], project_path: Path = None):
        """
        Initialize the configuration editor.
        
        Args:
            parent: Parent window
            current_config: Current configuration dictionary
            project_path: Path to the project (for saving config)
        """
        self.parent = parent
        self.current_config = current_config
        self.project_path = project_path
        self.result = None
        self.field_widgets = {}
        
        # Create dialog
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration Editor")
        self.dialog.geometry("700x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self._create_widgets()
        self._load_values()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Info label
        info_frame = ttk.Frame(self.dialog)
        info_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Label(
            info_frame,
            text="Configure linter settings. Changes will be saved to pyproject.toml.",
            font=('Arial', 9)
        ).pack(anchor=W)
        
        # Notebook for different linter categories
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=BOTH, expand=YES, padx=10, pady=5)
        
        # Create a tab for each linter
        for linter_name, config in self.CONFIG_SCHEMA.items():
            tab = self._create_linter_tab(notebook, linter_name, config)
            notebook.add(tab, text=linter_name)
        
        # Button frame
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save,
            bootstyle=SUCCESS
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            bootstyle=SECONDARY
        ).pack(side=RIGHT, padx=5)
        
        ttk.Button(
            button_frame,
            text="Reset to Defaults",
            command=self._on_reset,
            bootstyle=WARNING
        ).pack(side=LEFT, padx=5)
    
    def _create_linter_tab(self, notebook, linter_name: str, config: Dict) -> ttk.Frame:
        """Create a tab for a specific linter."""
        tab = ttk.Frame(notebook)
        
        # Scrollable frame
        canvas = tk.Canvas(tab, highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=LEFT, fill=BOTH, expand=YES)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Add fields
        section = config["section"]
        
        ttk.Label(
            scrollable_frame,
            text=f"{linter_name} Configuration",
            font=('Arial', 11, 'bold')
        ).pack(anchor=W, padx=10, pady=(10, 20))
        
        for field_name, field_type, default_value, description in config["fields"]:
            self._create_field(scrollable_frame, section, field_name, field_type, 
                             default_value, description)
        
        return tab
    
    def _create_field(self, parent, section: str, field_name: str, field_type: str,
                      default_value: Any, description: str):
        """Create a configuration field."""
        field_frame = ttk.Frame(parent)
        field_frame.pack(fill=X, padx=10, pady=5)
        
        # Label
        label_text = field_name.replace('_', ' ').title()
        ttk.Label(
            field_frame,
            text=label_text + ":",
            width=25,
            font=('Arial', 9, 'bold')
        ).pack(side=LEFT, padx=5)
        
        # Input widget based on type
        key = f"{section}.{field_name}"
        
        if field_type == "bool":
            var = tk.BooleanVar(value=default_value)
            widget = ttk.Checkbutton(field_frame, variable=var, bootstyle="success-round-toggle")
            widget.pack(side=LEFT, padx=5)
            self.field_widgets[key] = (var, field_type)
            
        elif field_type == "int":
            var = tk.StringVar(value=str(default_value))
            widget = ttk.Entry(field_frame, textvariable=var, width=15)
            widget.pack(side=LEFT, padx=5)
            self.field_widgets[key] = (var, field_type)
            
        elif field_type == "float":
            var = tk.StringVar(value=str(default_value))
            widget = ttk.Entry(field_frame, textvariable=var, width=15)
            widget.pack(side=LEFT, padx=5)
            self.field_widgets[key] = (var, field_type)
            
        elif field_type == "list":
            var = tk.StringVar(value=default_value if isinstance(default_value, str) else ", ".join(default_value))
            widget = ttk.Entry(field_frame, textvariable=var, width=30)
            widget.pack(side=LEFT, padx=5)
            self.field_widgets[key] = (var, field_type)
        
        # Description
        desc_frame = ttk.Frame(parent)
        desc_frame.pack(fill=X, padx=10, pady=(0, 10))
        
        ttk.Label(
            desc_frame,
            text=f"   {description}",
            font=('Arial', 8),
            foreground='gray'
        ).pack(anchor=W)
    
    def _load_values(self):
        """Load current configuration values into widgets."""
        for key, (var, field_type) in self.field_widgets.items():
            section, field = key.split('.', 1)
            
            # Get value from current config
            value = None
            if section in self.current_config:
                value = self.current_config[section].get(field)
            
            if value is not None:
                if field_type == "bool":
                    var.set(bool(value))
                elif field_type in ["int", "float"]:
                    var.set(str(value))
                elif field_type == "list":
                    if isinstance(value, list):
                        var.set(", ".join(value))
                    else:
                        var.set(str(value))
    
    def _get_values(self) -> Dict[str, Any]:
        """Get configuration values from widgets."""
        config = {}
        
        for key, (var, field_type) in self.field_widgets.items():
            section, field = key.split('.', 1)
            
            if section not in config:
                config[section] = {}
            
            try:
                if field_type == "bool":
                    config[section][field] = var.get()
                elif field_type == "int":
                    config[section][field] = int(var.get())
                elif field_type == "float":
                    config[section][field] = float(var.get())
                elif field_type == "list":
                    value = var.get()
                    config[section][field] = [v.strip() for v in value.split(',')]
            except ValueError as e:
                raise ValueError(f"Invalid value for {field}: {e}")
        
        return config
    
    def _on_save(self):
        """Handle save button."""
        try:
            self.result = self._get_values()
            self.dialog.destroy()
        except ValueError as e:
            messagebox.showerror("Invalid Configuration", str(e))
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()
    
    def _on_reset(self):
        """Reset all values to defaults."""
        if messagebox.askyesno("Reset Configuration", 
                              "Reset all settings to default values?"):
            for key, (var, field_type) in self.field_widgets.items():
                # Find default value
                for linter_config in self.CONFIG_SCHEMA.values():
                    section = linter_config["section"]
                    field_name = key.split('.', 1)[1]
                    
                    for fname, ftype, default, desc in linter_config["fields"]:
                        if fname == field_name:
                            if field_type == "bool":
                                var.set(default)
                            elif field_type in ["int", "float"]:
                                var.set(str(default))
                            elif field_type == "list":
                                if isinstance(default, list):
                                    var.set(", ".join(default))
                                else:
                                    var.set(str(default))
                            break
    
    def show(self) -> Dict[str, Any]:
        """
        Show the dialog and wait for result.
        
        Returns:
            Configuration dictionary or None if cancelled
        """
        self.dialog.wait_window()
        return self.result

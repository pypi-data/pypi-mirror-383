"""Menu Bar component."""

import tkinter as tk


class MenuBar:
    """Menu bar for the application."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the menu bar.
        
        Args:
            root: The root window
        """
        self.root = root
        self.menubar = tk.Menu(root)
        root.config(menu=self.menubar)
        
        # Callbacks
        self._open_folder_callback = None
        self._analyze_callback = None
        self._save_report_callback = None
        self._exit_callback = None
        self._copy_callback = None
        self._config_callback = None
        
        self._create_menus()
    
    def _create_menus(self):
        """Create menu structure."""
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Folder...", command=self._on_open_folder, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Analyze", command=self._on_analyze, accelerator="F5", state='disabled')
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Save Report...", command=self._on_save_report, accelerator="Ctrl+S", state='disabled')
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self._on_exit, accelerator="Alt+F4")
        
        # Edit menu
        self.edit_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Copy", command=self._on_copy, accelerator="Ctrl+C")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Configuration...", command=self._on_config)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self._on_open_folder())
        self.root.bind('<F5>', lambda e: self._on_analyze())
        self.root.bind('<Control-s>', lambda e: self._on_save_report())
        self.root.bind('<Control-c>', lambda e: self._on_copy())
    
    def _on_open_folder(self):
        if self._open_folder_callback:
            self._open_folder_callback()
    
    def _on_analyze(self):
        if self._analyze_callback:
            self._analyze_callback()
    
    def _on_save_report(self):
        if self._save_report_callback:
            self._save_report_callback()
    
    def _on_exit(self):
        if self._exit_callback:
            self._exit_callback()
    
    def _on_copy(self):
        if self._copy_callback:
            self._copy_callback()
    
    def _on_config(self):
        if self._config_callback:
            self._config_callback()
    
    def set_open_folder_callback(self, callback):
        self._open_folder_callback = callback
    
    def set_analyze_callback(self, callback):
        self._analyze_callback = callback
    
    def set_save_report_callback(self, callback):
        self._save_report_callback = callback
    
    def set_exit_callback(self, callback):
        self._exit_callback = callback
    
    def set_copy_callback(self, callback):
        self._copy_callback = callback
    
    def set_config_callback(self, callback):
        self._config_callback = callback
    
    def enable_analyze(self, enabled: bool = True):
        """Enable/disable analyze menu item."""
        self.file_menu.entryconfig("Analyze", state='normal' if enabled else 'disabled')
    
    def enable_save_report(self, enabled: bool = True):
        """Enable/disable save report menu item."""
        self.file_menu.entryconfig("Save Report...", state='normal' if enabled else 'disabled')

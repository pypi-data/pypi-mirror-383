"""Status Bar component."""

from tkinter import ttk
from ttkbootstrap.constants import *


class StatusBar:
    """Status bar at the bottom of the window."""
    
    def __init__(self, root):
        """
        Initialize the status bar.
        
        Args:
            root: The root window
        """
        self.frame = ttk.Frame(root)
        
        # Status label
        self.status_label = ttk.Label(self.frame, text="Ready", anchor=W)
        self.status_label.pack(side=LEFT, fill=X, expand=YES, padx=5)
        
        # Info labels
        self.file_count_label = ttk.Label(self.frame, text="Files: 0", width=12)
        self.file_count_label.pack(side=RIGHT, padx=5)
        
        self.violation_count_label = ttk.Label(self.frame, text="Violations: 0", width=15)
        self.violation_count_label.pack(side=RIGHT, padx=5)
    
    def set_status(self, message: str):
        """
        Update the status message.
        
        Args:
            message: Status message to display
        """
        self.status_label.config(text=message)
        self.status_label.update_idletasks()
    
    def set_file_count(self, count: int):
        """
        Update the file count display.
        
        Args:
            count: Number of files
        """
        self.file_count_label.config(text=f"Files: {count}")
    
    def set_violation_count(self, count: int):
        """
        Update the violation count display.
        
        Args:
            count: Number of violations
        """
        self.violation_count_label.config(text=f"Violations: {count}")

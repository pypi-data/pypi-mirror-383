"""Progress Dialog - modal progress window with cancel."""

import tkinter as tk
from tkinter import ttk
from ttkbootstrap.constants import *


class ProgressDialog:
    """Modal progress dialog with cancel button."""
    
    def __init__(self, parent, title="Processing..."):
        """
        Initialize the progress dialog.
        
        Args:
            parent: Parent window
            title: Dialog title
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 400) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 150) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.cancelled = False
        self._cancel_callback = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Message label
        self.message_label = ttk.Label(
            self.dialog,
            text="Initializing...",
            font=('Arial', 10)
        )
        self.message_label.pack(pady=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(
            self.dialog,
            mode='determinate',
            length=350
        )
        self.progress.pack(pady=10)
        
        # Cancel button
        self.cancel_btn = ttk.Button(
            self.dialog,
            text="Cancel",
            command=self._on_cancel,
            bootstyle=DANGER
        )
        self.cancel_btn.pack(pady=10)
    
    def _on_cancel(self):
        """Handle cancel button click."""
        self.cancelled = True
        self.cancel_btn.config(state='disabled', text="Cancelling...")
        if self._cancel_callback:
            self._cancel_callback()
    
    def set_cancel_callback(self, callback):
        """Set callback for cancel action."""
        self._cancel_callback = callback
    
    def update_progress(self, message: str, percent: int):
        """
        Update progress display.
        
        Args:
            message: Status message
            percent: Progress percentage (0-100)
        """
        self.message_label.config(text=message)
        self.progress['value'] = percent
        self.dialog.update()
    
    def close(self):
        """Close the dialog."""
        self.dialog.grab_release()
        self.dialog.destroy()

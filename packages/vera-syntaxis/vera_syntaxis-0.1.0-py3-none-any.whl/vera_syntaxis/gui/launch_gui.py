"""Launch script for Vera Syntaxis GUI."""

import sys

# Ensure ttkbootstrap is available
try:
    import ttkbootstrap as tb
except ImportError:
    print("Error: ttkbootstrap is required. Install it with:")
    print("  pip install ttkbootstrap")
    sys.exit(1)

# Ensure pygments is available
try:
    import pygments
except ImportError:
    print("Error: pygments is required. Install it with:")
    print("  pip install pygments")
    sys.exit(1)

# Import GUI components
from vera_syntaxis.gui.view.main_window import MainWindow
from vera_syntaxis.gui.controller.app_controller import AppController


def main():
    """Main entry point for the GUI application."""
    try:
        # Create root window with ttkbootstrap theme
        root = tb.Window(themename="flatly")
        
        # Create view
        view = MainWindow(root)
        
        # Create controller and bind to view
        controller = AppController(view)
        view.set_controller(controller)
        
        # Start the application
        view.run()
        
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

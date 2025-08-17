#!/usr/bin/env python3
"""
Main entry point for the Ark Survival: Ascended Discord Bot Management Application
"""

import tkinter as tk
from gui.main_window import MainWindow
import sys
import os

def main():
    """Initialize and run the main application"""
    try:
        # Create the main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

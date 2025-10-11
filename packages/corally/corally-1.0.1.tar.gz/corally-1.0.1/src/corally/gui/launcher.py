#!/usr/bin/env python3
"""
GUI Launcher for Calculator Suite
Modern replacement for Hauptprogramm.py
"""

import tkinter as tk
from tkinter import messagebox
import sys

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import requests  # noqa: F401
    except ImportError:
        missing_deps.append("requests")
    
    try:
        import uvicorn  # noqa: F401
    except ImportError:
        missing_deps.append("uvicorn")
    
    try:
        import fastapi  # noqa: F401
    except ImportError:
        missing_deps.append("fastapi")
    
    try:
        import httpx  # noqa: F401
    except ImportError:
        missing_deps.append("httpx")
    
    try:
        import dotenv  # noqa: F401
    except ImportError:
        missing_deps.append("python-dotenv")
    
    if missing_deps:
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        deps_str = ", ".join(missing_deps)
        message = f"""Missing dependencies: {deps_str}

To install them, run:
pip install {" ".join(missing_deps)}

Would you like to continue anyway? 
(Some features may not work)"""
        
        result = messagebox.askyesno("Missing Dependencies", message)
        root.destroy()
        
        if not result:
            sys.exit(1)

def main():
    """Main function to launch the calculator GUI"""
    # Check dependencies first
    check_dependencies()
    
    # Check if core modules can be imported
    try:
        from ..core import CalculatorCore, CurrencyConverter, InterestCalculator
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error",
                           f"Failed to import core calculator modules: {str(e)}\n\n"
                           f"Please make sure the corally package is properly installed.")
        root.destroy()
        sys.exit(1)
    
    # Import and launch the GUI
    try:
        from .main import ModernCalculatorGUI
        
        root = tk.Tk()
        app = ModernCalculatorGUI(root)
        
        # Handle window closing
        def on_closing():
            if hasattr(app, 'api_server_running') and app.api_server_running:
                app.stop_api_server()
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Center the window
        root.update_idletasks()
        width = root.winfo_width()
        height = root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")
        
        print("🚀 Calculator Suite GUI launched successfully!")
        print("📊 Features available:")
        print("   • Basic Calculator with logging")
        print("   • Currency Converter (static rates)")
        print("   • Interest Calculator")
        print("   • Live Currency API (requires API key)")
        print("\n💡 Tip: For live currency conversion, make sure you have a valid API key in your .env file")
        
        root.mainloop()
        
    except ImportError as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Import Error", 
                           f"Failed to import calculator GUI: {str(e)}\n\n"
                           f"Please make sure the corally package is properly installed.")
        root.destroy()
        sys.exit(1)
    except Exception as e:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to launch GUI: {str(e)}")
        root.destroy()
        sys.exit(1)

def launch_gui():
    """Launch the GUI application."""
    main()


if __name__ == "__main__":
    main()

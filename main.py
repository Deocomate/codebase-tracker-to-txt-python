import os
import mimetypes

# Use TkinterDnD for drag and drop support
from tkinterdnd2 import TkinterDnD
from ui import CodebaseTrackerUI


def main():
    # Initialize mimetypes
    mimetypes.init()

    # Create the main window with DnD support
    root = TkinterDnD.Tk()
    root.title("Codebase Tracker")

    # Set app icon (if available)
    try:
        # For Windows
        if os.name == 'nt':
            root.iconbitmap(default='icon.ico')
        # For Linux/Mac
        else:
            import tkinter as tk
            logo = tk.PhotoImage(file='icon.png')
            root.iconphoto(True, logo)
    except Exception:
        pass  # Icon not critical, proceed without it

    # Apply a theme if available
    try:
        import tkinter.ttk as ttk

        style = ttk.Style()
        available_themes = style.theme_names()

        # Choose a modern theme if available
        preferred_themes = ['clam', 'alt', 'vista', 'xpnative']
        for theme in preferred_themes:
            if theme in available_themes:
                style.theme_use(theme)
                break
    except Exception as e:
        print(f"Could not apply theme: {e}")

    # Create and run the application
    app = CodebaseTrackerUI(root)

    # Start the main loop
    root.mainloop()


if __name__ == "__main__":
    main()

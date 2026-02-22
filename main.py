import os
import sys
import mimetypes
from tkinterdnd2 import TkinterDnD
from app.gui.ui import CodebaseTrackerUI


def get_resource_path(filename: str) -> str:
    """Get absolute path to resource, works for dev and PyInstaller."""
    if getattr(sys, 'frozen', False):
        # Running as bundled executable
        base_path = sys._MEIPASS
    else:
        # Running in development
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


def main():
    mimetypes.init()
    root = TkinterDnD.Tk()

    try:
        if os.name == 'nt':
            icon_path = get_resource_path('icon.ico')
            root.iconbitmap(default=icon_path)
        else:
            import tkinter as tk
            icon_path = get_resource_path('icon.png')
            logo = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, logo)
    except Exception as e:
        print(f"Icon not found: {e}, proceeding without it.")

    app = CodebaseTrackerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

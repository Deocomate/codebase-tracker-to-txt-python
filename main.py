import os
import mimetypes
from tkinterdnd2 import TkinterDnD
from ui import CodebaseTrackerUI


def main():
    mimetypes.init()

    root = TkinterDnD.Tk()

    try:
        if os.name == 'nt':
            root.iconbitmap(default='icon.ico')
        else:
            import tkinter as tk
            logo = tk.PhotoImage(file='icon.png')
            root.iconphoto(True, logo)
    except Exception:
        print("Icon not found, proceeding without it.")

    app = CodebaseTrackerUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

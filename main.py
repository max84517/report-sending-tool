"""
Entry point for the Report Sending Tool.
"""
import tkinter as tk
from ui.main_window import MainWindow


def main():
    root = tk.Tk()
    root.tk_setPalette(
        background="#1e1e1e",
        foreground="#e0e0e0",
        activeBackground="#3a3a3a",
        activeForeground="#e0e0e0",
    )
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()

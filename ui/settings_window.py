"""
Settings window — user profile configuration.
"""
import tkinter as tk
from tkinter import messagebox
import sys, os

# ── Dark palette ──────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
FG       = "#e0e0e0"
ENTRY_BG = "#2d2d2d"
ACCENT   = "#0078d4"
HOVER    = "#005a9e"
BTN_BG   = "#3a3a3a"
BORDER   = "#4a4a4a"


def _style_btn(btn, bg=BTN_BG, hover=HOVER):
    btn.configure(bg=bg, fg=FG, relief="flat", bd=0,
                  activebackground=hover, activeforeground=FG,
                  cursor="hand2", padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))


class SettingsWindow(tk.Toplevel):
    """
    User settings dialog.
    Edits the given StringVar in-place and calls on_save() when confirmed.
    """

    def __init__(self, parent, user_name_var: tk.StringVar, on_save):
        super().__init__(parent)
        self.title("Settings")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()

        self._user_name_var = user_name_var
        self._on_save = on_save

        self._build_ui()
        self._center(parent)

    def _build_ui(self):
        # ── Header ────────────────────────────────────────────────────────────
        header = tk.Frame(self, bg="#1a1a2e")
        header.pack(fill="x")
        tk.Label(header, text="  Settings", bg="#1a1a2e", fg=FG,
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=10, padx=4)

        # ── Form ──────────────────────────────────────────────────────────────
        form = tk.Frame(self, bg=BG)
        form.pack(fill="x", padx=24, pady=(20, 8))

        tk.Label(form, text="Your Name", bg=BG, fg=FG,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=0,
                 sticky="w", pady=(0, 4))
        tk.Label(form, text="Required — appears in the email sign-off.",
                 bg=BG, fg="#888888", font=("Segoe UI", 9)
                 ).grid(row=1, column=0, sticky="w", pady=(0, 8))

        self._name_entry = tk.Entry(
            form, textvariable=self._user_name_var,
            bg=ENTRY_BG, fg=FG, insertbackground=FG,
            relief="flat", bd=1, font=("Segoe UI", 11), width=34,
            highlightbackground=BORDER, highlightthickness=1,
        )
        self._name_entry.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        self._name_entry.focus_set()

        # ── Hint ──────────────────────────────────────────────────────────────
        hint_frame = tk.Frame(self, bg="#252526")
        hint_frame.pack(fill="x", padx=24, pady=(8, 0))
        tk.Label(hint_frame, text="Email sign-off preview:", bg="#252526",
                 fg="#888888", font=("Segoe UI", 9)).pack(anchor="w", pady=(6, 2))

        self._preview_var = tk.StringVar()
        tk.Label(hint_frame, textvariable=self._preview_var, bg="#252526",
                 fg="#4ec9b0", font=("Consolas", 10),
                 justify="left", anchor="w").pack(anchor="w", padx=8, pady=(0, 8))

        self._user_name_var.trace_add("write", self._update_preview)
        self._update_preview()

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=24, pady=(8, 20))

        save_btn = tk.Button(btn_row, text="Save", command=self._save,
                             font=("Segoe UI", 10, "bold"))
        _style_btn(save_btn, bg=ACCENT, hover=HOVER)
        save_btn.pack(side="right", padx=(8, 0))

        cancel_btn = tk.Button(btn_row, text="Cancel", command=self.destroy,
                               font=("Segoe UI", 10))
        _style_btn(cancel_btn)
        cancel_btn.pack(side="right")

        form.columnconfigure(0, weight=1)

    def _update_preview(self, *_):
        name = self._user_name_var.get().strip() or "<Your Name>"
        self._preview_var.set(f"Best Regards,\n{name}")

    def _save(self):
        name = self._user_name_var.get().strip()
        if not name:
            messagebox.showwarning("Name required",
                                   "Please enter your name before saving.",
                                   parent=self)
            self._name_entry.focus_set()
            return
        self._on_save()
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h   = self.winfo_reqwidth(), self.winfo_reqheight()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")

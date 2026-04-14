import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from modules.contacts_manager import load_contacts, save_contacts

# ── Dark palette ──────────────────────────────────────────────────────────────
BG = "#1e1e1e"
FG = "#e0e0e0"
ENTRY_BG = "#2d2d2d"
ACCENT = "#0078d4"
HOVER = "#005a9e"
BTN_BG = "#3a3a3a"
SEL_BG = "#0078d4"
BORDER = "#4a4a4a"
RED = "#c0392b"
RED_HOVER = "#922b21"


def _style_btn(btn, bg=BTN_BG, hover=HOVER):
    btn.configure(bg=bg, fg=FG, relief="flat", bd=0,
                  activebackground=hover, activeforeground=FG,
                  cursor="hand2", padx=10, pady=5)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))


class ContactDialog(tk.Toplevel):
    """Add / Edit a single contact."""

    def __init__(self, parent, contact: dict | None = None):
        super().__init__(parent)
        self.title("Edit Contact" if contact else "Add Contact")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()
        self.result: dict | None = None

        fields = [("Name", "name"), ("Company", "company"), ("Email", "email")]
        self._vars = {}

        for row, (label, key) in enumerate(fields):
            tk.Label(self, text=label, bg=BG, fg=FG, font=("Segoe UI", 10)
                     ).grid(row=row, column=0, padx=(16, 8), pady=8, sticky="e")
            var = tk.StringVar(value=contact.get(key, "") if contact else "")
            self._vars[key] = var
            entry = tk.Entry(self, textvariable=var, bg=ENTRY_BG, fg=FG,
                             insertbackground=FG, relief="flat", bd=1,
                             font=("Segoe UI", 10), width=30,
                             highlightbackground=BORDER, highlightthickness=1)
            entry.grid(row=row, column=1, padx=(0, 16), pady=8, sticky="ew")

        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=(4, 16))

        save_btn = tk.Button(btn_frame, text="Save", command=self._save,
                             font=("Segoe UI", 10, "bold"))
        _style_btn(save_btn, bg=ACCENT, hover=HOVER)
        save_btn.pack(side="left", padx=6)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.destroy,
                               font=("Segoe UI", 10))
        _style_btn(cancel_btn)
        cancel_btn.pack(side="left", padx=6)

        self.columnconfigure(1, weight=1)
        self._center(parent)

    def _save(self):
        name = self._vars["name"].get().strip()
        company = self._vars["company"].get().strip()
        email = self._vars["email"].get().strip()
        if not name or not email:
            messagebox.showwarning("Missing fields", "Name and Email are required.", parent=self)
            return
        self.result = {"name": name, "company": company, "email": email}
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        px, py = parent.winfo_rootx(), parent.winfo_rooty()
        pw, ph = parent.winfo_width(), parent.winfo_height()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")


class ContactsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Contacts Manager")
        self.configure(bg=BG)
        self.geometry("640x480")
        self.minsize(500, 360)
        self.grab_set()

        self._build_ui()
        self._refresh()

    # ── UI ────────────────────────────────────────────────────────────────────
    def _build_ui(self):
        top = tk.Frame(self, bg=BG)
        top.pack(fill="x", padx=16, pady=(14, 6))

        tk.Label(top, text="Contacts", bg=BG, fg=FG,
                 font=("Segoe UI", 14, "bold")).pack(side="left")

        add_btn = tk.Button(top, text="+ Add", command=self._add,
                            font=("Segoe UI", 10, "bold"))
        _style_btn(add_btn, bg=ACCENT, hover=HOVER)
        add_btn.pack(side="right")

        # ── Table ─────────────────────────────────────────────────────────────
        cols = ("name", "company", "email")
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Dark.Treeview",
                        background=ENTRY_BG, foreground=FG,
                        fieldbackground=ENTRY_BG, rowheight=28,
                        font=("Segoe UI", 10))
        style.configure("Dark.Treeview.Heading",
                        background=BTN_BG, foreground=FG,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Dark.Treeview",
                  background=[("selected", SEL_BG)],
                  foreground=[("selected", "#ffffff")])

        frame = tk.Frame(self, bg=BG)
        frame.pack(fill="both", expand=True, padx=16, pady=4)

        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 style="Dark.Treeview", selectmode="browse")
        widths = {"name": 160, "company": 180, "email": 240}
        for col in cols:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=widths[col], anchor="w")

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # ── Action buttons ────────────────────────────────────────────────────
        btn_frame = tk.Frame(self, bg=BG)
        btn_frame.pack(fill="x", padx=16, pady=(4, 14))

        edit_btn = tk.Button(btn_frame, text="Edit Selected",
                             command=self._edit, font=("Segoe UI", 10))
        _style_btn(edit_btn)
        edit_btn.pack(side="left", padx=(0, 8))

        del_btn = tk.Button(btn_frame, text="Delete Selected",
                            command=self._delete, font=("Segoe UI", 10))
        _style_btn(del_btn, bg=RED, hover=RED_HOVER)
        del_btn.pack(side="left")

    # ── Data operations ───────────────────────────────────────────────────────
    def _refresh(self):
        self.tree.delete(*self.tree.get_children())
        for c in load_contacts():
            self.tree.insert("", "end",
                             values=(c.get("name", ""),
                                     c.get("company", ""),
                                     c.get("email", "")))

    def _selected_index(self) -> int | None:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select a contact first.", parent=self)
            return None
        return self.tree.index(sel[0])

    def _add(self):
        dlg = ContactDialog(self)
        self.wait_window(dlg)
        if dlg.result:
            contacts = load_contacts()
            contacts.append(dlg.result)
            save_contacts(contacts)
            self._refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return
        contacts = load_contacts()
        dlg = ContactDialog(self, contacts[idx])
        self.wait_window(dlg)
        if dlg.result:
            contacts[idx] = dlg.result
            save_contacts(contacts)
            self._refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return
        contacts = load_contacts()
        name = contacts[idx].get("name", "?")
        if messagebox.askyesno("Confirm Delete",
                                f"Delete contact '{name}'?", parent=self):
            contacts.pop(idx)
            save_contacts(contacts)
            self._refresh()

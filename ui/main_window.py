"""
Main application window — report sending tool.
"""
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys, os
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from modules.file_scanner     import scan_reports
from modules.contacts_manager import find_contacts_by_supplier
from modules.draft_manager    import load_draft
from modules.outlook_sender   import send_email
from ui.contacts_window       import ContactsWindow
from ui.draft_window          import DraftEditorWindow
from ui.settings_window       import SettingsWindow

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

# ── Dark palette ──────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
PANEL_BG = "#252526"
FG       = "#e0e0e0"
ENTRY_BG = "#2d2d2d"
ACCENT   = "#0078d4"
HOVER    = "#005a9e"
BTN_BG   = "#3a3a3a"
BORDER   = "#4a4a4a"
GREEN    = "#27ae60"
GREEN_H  = "#1e8449"
RED      = "#c0392b"
RED_H    = "#922b21"
SEL_BG   = "#0078d4"


def _style_btn(btn, bg=BTN_BG, hover=HOVER):
    btn.configure(bg=bg, fg=FG, relief="flat", bd=0,
                  activebackground=hover, activeforeground=FG,
                  cursor="hand2", padx=10, pady=6)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))


class MainWindow:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Report Sending Tool")
        self.root.configure(bg=BG)
        self.root.geometry("860x620")
        self.root.minsize(700, 500)

        self._folder_var  = tk.StringVar()
        self._send_mode   = tk.StringVar(value="draft")
        self._user_name   = tk.StringVar()
        self._report_rows: list[dict] = []  # {filename, supplier, filepath, var(BoolVar)}

        self._build_ui()
        self._load_config()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root

        # ── Title bar ─────────────────────────────────────────────────────────
        title_bar = tk.Frame(root, bg="#1a1a2e", height=42)
        title_bar.pack(fill="x")
        tk.Label(title_bar, text="  Report Sending Tool", bg="#1a1a2e", fg=FG,
                 font=("Segoe UI", 13, "bold")).pack(side="left", pady=8)

        # ── Top controls ──────────────────────────────────────────────────────
        ctrl = tk.Frame(root, bg=BG)
        ctrl.pack(fill="x", padx=20, pady=(14, 6))

        # Folder selector
        folder_frame = tk.Frame(ctrl, bg=BG)
        folder_frame.pack(fill="x")

        tk.Label(folder_frame, text="Report Folder:", bg=BG, fg=FG,
                 font=("Segoe UI", 10)).pack(side="left")

        folder_entry = tk.Entry(folder_frame, textvariable=self._folder_var,
                                bg=ENTRY_BG, fg=FG, insertbackground=FG,
                                relief="flat", bd=1, font=("Segoe UI", 10),
                                highlightbackground=BORDER, highlightthickness=1,
                                readonlybackground=ENTRY_BG,
                                disabledbackground=ENTRY_BG, disabledforeground=FG,
                                state="readonly")
        folder_entry.pack(side="left", fill="x", expand=True, padx=(8, 6))

        browse_btn = tk.Button(folder_frame, text="Browse…",
                               command=self._browse_folder,
                               font=("Segoe UI", 10))
        _style_btn(browse_btn)
        browse_btn.pack(side="left")

        refresh_btn = tk.Button(folder_frame, text="↻ Refresh",
                                command=self._scan,
                                font=("Segoe UI", 10, "bold"))
        _style_btn(refresh_btn, bg=ACCENT, hover=HOVER)
        refresh_btn.pack(side="left", padx=(6, 0))

        # ── Action buttons row ────────────────────────────────────────────────
        action_row = tk.Frame(root, bg=BG)
        action_row.pack(fill="x", padx=20, pady=6)

        edit_draft_btn = tk.Button(action_row, text="✏  Edit Draft",
                                   command=self._open_draft_editor,
                                   font=("Segoe UI", 10))
        _style_btn(edit_draft_btn)
        edit_draft_btn.pack(side="left", padx=(0, 8))

        contacts_btn = tk.Button(action_row, text="👥  Edit Contacts",
                                 command=self._open_contacts,
                                 font=("Segoe UI", 10))
        _style_btn(contacts_btn)
        contacts_btn.pack(side="left", padx=(0, 8))

        settings_btn = tk.Button(action_row, text="⚙  Settings",
                                 command=self._open_settings,
                                 font=("Segoe UI", 10))
        _style_btn(settings_btn)
        settings_btn.pack(side="left", padx=(0, 8))

        # Send mode toggle
        draft_radio = tk.Radiobutton(action_row, text="Save as Draft",
                                     variable=self._send_mode, value="draft",
                                     bg=BG, fg=FG, selectcolor=ENTRY_BG,
                                     activebackground=BG, activeforeground=FG,
                                     font=("Segoe UI", 10),
                                     command=self._save_config)
        draft_radio.pack(side="left", padx=(16, 4))

        send_radio = tk.Radiobutton(action_row, text="Send Now",
                                    variable=self._send_mode, value="send",
                                    bg=BG, fg=FG, selectcolor=ENTRY_BG,
                                    activebackground=BG, activeforeground=FG,
                                    font=("Segoe UI", 10),
                                    command=self._save_config)
        send_radio.pack(side="left")

        go_btn = tk.Button(action_row, text="▶  Go",
                           command=self._go,
                           font=("Segoe UI", 10, "bold"))
        _style_btn(go_btn, bg=GREEN, hover=GREEN_H)
        go_btn.pack(side="right")

        # ── Report list header ────────────────────────────────────────────────
        list_header = tk.Frame(root, bg=PANEL_BG, pady=6)
        list_header.pack(fill="x", padx=20)

        tk.Label(list_header, text="Detected Reports", bg=PANEL_BG, fg=FG,
                 font=("Segoe UI", 10, "bold")).pack(side="left", padx=8)

        sel_all_btn = tk.Button(list_header, text="Select All",
                                command=self._select_all,
                                font=("Segoe UI", 9))
        _style_btn(sel_all_btn)
        sel_all_btn.pack(side="right", padx=(0, 8))

        desel_btn = tk.Button(list_header, text="Deselect All",
                              command=self._deselect_all,
                              font=("Segoe UI", 9))
        _style_btn(desel_btn)
        desel_btn.pack(side="right")

        # ── Scrollable report list ─────────────────────────────────────────────
        list_outer = tk.Frame(root, bg=PANEL_BG, relief="flat")
        list_outer.pack(fill="both", expand=True, padx=20, pady=(0, 4))

        canvas = tk.Canvas(list_outer, bg=PANEL_BG, highlightthickness=0)
        self._list_frame = tk.Frame(canvas, bg=PANEL_BG)
        vsb = ttk.Scrollbar(list_outer, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        self._canvas_win = canvas.create_window((0, 0), window=self._list_frame,
                                                anchor="nw")

        self._list_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(self._canvas_win, width=e.width))
        canvas.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # ── Status bar ────────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="Ready.")
        status_bar = tk.Label(root, textvariable=self._status_var,
                              bg="#007acc", fg="#ffffff",
                              font=("Segoe UI", 9), anchor="w", padx=12)
        status_bar.pack(fill="x", side="bottom")

    # ── Config persistence ────────────────────────────────────────────────────
    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                self._folder_var.set(cfg.get("folder_path", ""))
                self._send_mode.set(cfg.get("send_mode", "draft"))
                self._user_name.set(cfg.get("user_name", ""))
                if self._folder_var.get():
                    self._scan()
            except Exception:
                pass

        # Force user to set name on first launch
        if not self._user_name.get().strip():
            self.root.after(200, self._open_settings_required)

    def _save_config(self):
        cfg = {
            "folder_path": self._folder_var.get(),
            "send_mode": self._send_mode.get(),
            "user_name": self._user_name.get().strip(),
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)

    def _on_close(self):
        self._save_config()
        self.root.destroy()

    # ── Actions ───────────────────────────────────────────────────────────────
    def _browse_folder(self):
        path = filedialog.askdirectory(title="Select report base folder")
        if path:
            self._folder_var.set(path)
            self._save_config()
            self._scan()

    def _scan(self):
        base = self._folder_var.get().strip()
        if not base:
            messagebox.showwarning("No folder", "Please select a report folder first.")
            return
        reports = scan_reports(base)
        self._report_rows = []
        for w in self._list_frame.winfo_children():
            w.destroy()

        if not reports:
            tk.Label(self._list_frame, text="No reports found in the latest folder.",
                     bg=PANEL_BG, fg="#888888", font=("Segoe UI", 10)
                     ).pack(pady=20)
            self._status_var.set("Scan complete — no reports found.")
            return

        for r in reports:
            var = tk.BooleanVar(value=True)
            row = {**r, "var": var}
            self._report_rows.append(row)
            self._add_report_row(row)

        self._status_var.set(f"Scan complete — {len(reports)} report(s) found.")

    def _add_report_row(self, row: dict):
        frame = tk.Frame(self._list_frame, bg=PANEL_BG)
        frame.pack(fill="x", padx=8, pady=2)

        chk = tk.Checkbutton(frame, variable=row["var"],
                             bg=PANEL_BG, fg=FG, selectcolor=ENTRY_BG,
                             activebackground=PANEL_BG, activeforeground=FG,
                             cursor="hand2")
        chk.pack(side="left")

        tk.Label(frame, text=row["filename"], bg=PANEL_BG, fg=FG,
                 font=("Consolas", 10), anchor="w").pack(side="left", padx=(4, 12))

        # Resolve all contacts for this supplier
        contacts = find_contacts_by_supplier(row["supplier"])
        if contacts:
            names = ", ".join(c["name"] for c in contacts)
            emails = ", ".join(c["email"] for c in contacts)
            info = f"→  {names}  <{emails}>"
            col  = "#4ec9b0"
        else:
            info = "→  No contact registered"
            col  = "#888888"

        tk.Label(frame, text=info, bg=PANEL_BG, fg=col,
                 font=("Segoe UI", 9), anchor="w").pack(side="left")

    def _select_all(self):
        for r in self._report_rows:
            r["var"].set(True)

    def _deselect_all(self):
        for r in self._report_rows:
            r["var"].set(False)

    def _open_draft_editor(self):
        DraftEditorWindow(self.root)

    def _open_contacts(self):
        ContactsWindow(self.root)

    def _open_settings(self):
        SettingsWindow(self.root, self._user_name, self._save_config)

    def _open_settings_required(self):
        """Open settings and block until name is filled in."""
        messagebox.showinfo(
            "Setup Required",
            "Please enter your name in Settings before using the tool.",
            parent=self.root,
        )
        self._open_settings()

    # ── Send / Draft ─────────────────────────────────────────────────────────
    def _go(self):
        # Enforce user name
        if not self._user_name.get().strip():
            messagebox.showwarning(
                "Name Required",
                "Please set your name in Settings before sending emails.",
                parent=self.root,
            )
            self._open_settings()
            return

        selected = [r for r in self._report_rows if r["var"].get()]
        if not selected:
            messagebox.showinfo("Nothing selected", "Please select at least one report.")
            return

        draft  = load_draft()
        subject = draft.get("subject", "(no subject)")
        body    = draft.get("body", "")

        if not subject and not body:
            if not messagebox.askyesno("Empty draft",
                                       "The draft subject and body are empty. Continue?"):
                return

        mode   = self._send_mode.get()
        save_draft_flag = (mode == "draft")

        action_label = "Saving drafts" if save_draft_flag else "Sending emails"
        self._status_var.set(f"{action_label}…")
        self.root.update_idletasks()

        # Run in thread to keep UI responsive
        threading.Thread(
            target=self._send_thread,
            args=(selected, subject, body, save_draft_flag, self._user_name.get().strip()),
            daemon=True
        ).start()

    def _send_thread(self, reports: list[dict], subject: str,
                     body: str, save_as_draft: bool, user_name: str):
        results = {"ok": 0, "skip": 0, "fail": 0, "errors": []}

        # Group selected reports by supplier so each supplier gets ONE email
        by_supplier: dict[str, list[dict]] = defaultdict(list)
        for r in reports:
            by_supplier[r["supplier"]].append(r)

        for supplier, supplier_reports in by_supplier.items():
            contacts = find_contacts_by_supplier(supplier)
            if not contacts:
                results["skip"] += len(supplier_reports)
                continue
            try:
                to_list = [c["email"] for c in contacts]
                attachment_paths = [r["filepath"] for r in supplier_reports]
                # Replace {supplier} in body, then append sign-off
                main_body = body.replace("{supplier}", supplier)
                sign_off  = f"\n\nBest Regards,\n{user_name}"
                full_body  = main_body + sign_off
                send_email(
                    to_addresses     = to_list,
                    subject          = subject,
                    body_md          = full_body,
                    attachment_paths = attachment_paths,
                    save_as_draft    = save_as_draft,
                )
                results["ok"] += 1
            except Exception as exc:
                results["fail"] += 1
                results["errors"].append(f"{supplier}: {exc}")

        # Update UI from main thread
        self.root.after(0, self._show_results, results, save_as_draft)

    def _show_results(self, results: dict, save_as_draft: bool):
        action = "saved to Drafts" if save_as_draft else "sent"
        msg = (f"{results['ok']} email(s) {action}.\n"
               f"{results['skip']} skipped (no contact).\n"
               f"{results['fail']} failed.")
        if results["errors"]:
            msg += "\n\nErrors:\n" + "\n".join(results["errors"])
        title = "Done" if results["fail"] == 0 else "Completed with errors"
        messagebox.showinfo(title, msg, parent=self.root)
        self._status_var.set(
            f"Done: {results['ok']} {action}, "
            f"{results['skip']} skipped, {results['fail']} failed."
        )

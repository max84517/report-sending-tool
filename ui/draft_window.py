"""
Draft editor window — Markdown-aware rich text editor.

Toolbar supports:
  Bold, Italic, Bold+Italic, H1/H2/H3, colour picker, font picker
  and a live preview panel (Markdown → rendered via tkinter Tag styles).
"""
import tkinter as tk
from tkinter import font as tkfont, colorchooser, messagebox
import sys, os, re

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from modules.draft_manager import load_draft, save_draft

# ── Dark palette ──────────────────────────────────────────────────────────────
BG       = "#1e1e1e"
PANEL_BG = "#252526"
FG       = "#e0e0e0"
ENTRY_BG = "#2d2d2d"
ACCENT   = "#0078d4"
HOVER    = "#005a9e"
BTN_BG   = "#3a3a3a"
BORDER   = "#4a4a4a"
TOOLBAR  = "#2d2d2d"


def _style_btn(btn, bg=BTN_BG, hover=HOVER, relief="flat"):
    btn.configure(bg=bg, fg=FG, relief=relief, bd=0,
                  activebackground=hover, activeforeground=FG,
                  cursor="hand2", padx=8, pady=4)
    btn.bind("<Enter>", lambda e: btn.configure(bg=hover))
    btn.bind("<Leave>", lambda e: btn.configure(bg=bg))


class DraftEditorWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Edit Draft")
        self.configure(bg=BG)
        self.geometry("900x620")
        self.minsize(700, 450)

        draft = load_draft()
        self._subject_var = tk.StringVar(value=draft.get("subject", ""))
        self._body_md: str = draft.get("body", "")

        self._build_ui()
        self._text.insert("1.0", self._body_md)
        self._apply_highlighting()

    # ── Build ─────────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Subject row
        subj_frame = tk.Frame(self, bg=BG)
        subj_frame.pack(fill="x", padx=16, pady=(14, 4))
        tk.Label(subj_frame, text="Subject:", bg=BG, fg=FG,
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 8))
        subj_entry = tk.Entry(subj_frame, textvariable=self._subject_var,
                              bg=ENTRY_BG, fg=FG, insertbackground=FG,
                              relief="flat", bd=1, font=("Segoe UI", 10),
                              highlightbackground=BORDER, highlightthickness=1)
        subj_entry.pack(side="left", fill="x", expand=True)

        # Toolbar
        toolbar = tk.Frame(self, bg=TOOLBAR, pady=4)
        toolbar.pack(fill="x", padx=16)
        self._build_toolbar(toolbar)

        # Editor + preview side by side
        pane = tk.PanedWindow(self, orient="horizontal",
                              bg=BG, sashwidth=4, sashrelief="flat")
        pane.pack(fill="both", expand=True, padx=16, pady=6)

        # Left — raw markdown editor
        left = tk.Frame(pane, bg=BG)
        pane.add(left, stretch="always")
        tk.Label(left, text="Markdown", bg=BG, fg="#888888",
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._text = tk.Text(left, bg=ENTRY_BG, fg=FG, insertbackground=FG,
                             relief="flat", bd=0, font=("Consolas", 11),
                             undo=True, wrap="word",
                             selectbackground=ACCENT, selectforeground="#ffffff",
                             padx=8, pady=8)
        self._text.pack(fill="both", expand=True)
        self._text.bind("<KeyRelease>", lambda e: self._apply_highlighting())

        # Right — preview
        right = tk.Frame(pane, bg=BG)
        pane.add(right, stretch="always")
        tk.Label(right, text="Preview", bg=BG, fg="#888888",
                 font=("Segoe UI", 9)).pack(anchor="w")
        self._preview = tk.Text(right, bg=PANEL_BG, fg=FG,
                                relief="flat", bd=0, font=("Segoe UI", 11),
                                state="disabled", wrap="word",
                                padx=10, pady=8)
        self._preview.pack(fill="both", expand=True)
        self._setup_preview_tags()
        self._text.bind("<KeyRelease>", lambda e: (self._apply_highlighting(), self._refresh_preview()))
        self._refresh_preview()

        # Bottom buttons
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=16, pady=(0, 14))

        save_btn = tk.Button(btn_row, text="Save Draft", command=self._save,
                             font=("Segoe UI", 10, "bold"))
        _style_btn(save_btn, bg=ACCENT, hover=HOVER)
        save_btn.pack(side="right", padx=(8, 0))

        cancel_btn = tk.Button(btn_row, text="Discard", command=self.destroy,
                               font=("Segoe UI", 10))
        _style_btn(cancel_btn)
        cancel_btn.pack(side="right")

        # ── Markdown highlight tags ────────────────────────────────────────────
        self._text.tag_configure("heading", foreground="#569cd6",
                                 font=("Consolas", 13, "bold"))
        self._text.tag_configure("bold", font=("Consolas", 11, "bold"))
        self._text.tag_configure("italic", font=("Consolas", 11, "italic"))
        self._text.tag_configure("bold_italic",
                                 font=("Consolas", 11, "bold italic"))
        self._text.tag_configure("color_tag", foreground="#ce9178")

    def _build_toolbar(self, parent):
        buttons = [
            ("B",  "bold",       self._wrap_bold),
            ("I",  "italic",     self._wrap_italic),
            ("B+I","bold+italic",self._wrap_bold_italic),
            ("H1", "heading1",   lambda: self._wrap_heading(1)),
            ("H2", "heading2",   lambda: self._wrap_heading(2)),
            ("H3", "heading3",   lambda: self._wrap_heading(3)),
        ]
        for label, _, cmd in buttons:
            b = tk.Button(parent, text=label, command=cmd,
                          font=("Segoe UI", 9, "bold"), width=4)
            _style_btn(b)
            b.pack(side="left", padx=2)

        # Separator
        tk.Label(parent, text="|", bg=TOOLBAR, fg="#555").pack(side="left", padx=4)

        # Colour picker
        color_btn = tk.Button(parent, text="Color", command=self._insert_color,
                              font=("Segoe UI", 9))
        _style_btn(color_btn)
        color_btn.pack(side="left", padx=2)

        # Font size spinbox
        tk.Label(parent, text="Font:", bg=TOOLBAR, fg=FG,
                 font=("Segoe UI", 9)).pack(side="left", padx=(12, 2))
        self._font_size = tk.IntVar(value=11)
        spin = tk.Spinbox(parent, from_=8, to=36, width=4, textvariable=self._font_size,
                          bg=ENTRY_BG, fg=FG, buttonbackground=BTN_BG,
                          relief="flat", font=("Segoe UI", 9),
                          command=self._apply_font_size)
        spin.pack(side="left")

    # ── Toolbar actions ───────────────────────────────────────────────────────
    def _selection_or_word(self) -> tuple[str, str]:
        """Return (start_index, end_index) for current selection or word at cursor."""
        try:
            return self._text.index("sel.first"), self._text.index("sel.last")
        except tk.TclError:
            idx = self._text.index("insert")
            return (self._text.index(f"{idx} wordstart"),
                    self._text.index(f"{idx} wordend"))

    def _wrap(self, prefix: str, suffix: str):
        start, end = self._selection_or_word()
        selected = self._text.get(start, end)
        self._text.delete(start, end)
        self._text.insert(start, f"{prefix}{selected}{suffix}")
        self._apply_highlighting()
        self._refresh_preview()

    def _wrap_bold(self):        self._wrap("**", "**")
    def _wrap_italic(self):      self._wrap("*", "*")
    def _wrap_bold_italic(self): self._wrap("***", "***")

    def _wrap_heading(self, level: int):
        hashes = "#" * level + " "
        try:
            start = self._text.index("sel.first linestart")
            end   = self._text.index("sel.last lineend")
        except tk.TclError:
            start = self._text.index("insert linestart")
            end   = self._text.index("insert lineend")
        line = self._text.get(start, end)
        line = re.sub(r"^#+\s*", "", line)
        self._text.delete(start, end)
        self._text.insert(start, hashes + line)
        self._apply_highlighting()
        self._refresh_preview()

    def _insert_color(self):
        color = colorchooser.askcolor(parent=self, title="Choose text colour")
        if not color or not color[1]:
            return
        hex_color = color[1]
        start, end = self._selection_or_word()
        selected = self._text.get(start, end)
        self._text.delete(start, end)
        self._text.insert(start, f"[color={hex_color}]{selected}[/color]")
        self._apply_highlighting()
        self._refresh_preview()

    def _apply_font_size(self):
        size = self._font_size.get()
        self._text.configure(font=("Consolas", size))

    # ── Syntax highlighting ───────────────────────────────────────────────────
    def _apply_highlighting(self):
        for tag in ("heading", "bold", "italic", "bold_italic", "color_tag"):
            self._text.tag_remove(tag, "1.0", "end")

        content = self._text.get("1.0", "end")

        patterns = [
            ("heading",    r"^#{1,6} .+$"),
            ("bold_italic",r"\*{3}.+?\*{3}"),
            ("bold",       r"\*{2}.+?\*{2}"),
            ("italic",     r"\*[^*\n]+?\*"),
            ("color_tag",  r"\[color=[^\]]+\].+?\[/color\]"),
        ]
        for tag, pattern in patterns:
            for m in re.finditer(pattern, content, re.MULTILINE | re.DOTALL if "color" in tag else re.MULTILINE):
                start = f"1.0 + {m.start()} chars"
                end   = f"1.0 + {m.end()} chars"
                self._text.tag_add(tag, start, end)

    # ── Preview ───────────────────────────────────────────────────────────────
    def _setup_preview_tags(self):
        self._preview.tag_configure("h1", font=("Segoe UI", 20, "bold"), spacing3=6)
        self._preview.tag_configure("h2", font=("Segoe UI", 16, "bold"), spacing3=4)
        self._preview.tag_configure("h3", font=("Segoe UI", 13, "bold"), spacing3=2)
        self._preview.tag_configure("bold",   font=("Segoe UI", 11, "bold"))
        self._preview.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        self._preview.tag_configure("bold_italic", font=("Segoe UI", 11, "bold italic"))

    def _refresh_preview(self):
        md = self._text.get("1.0", "end-1c")
        self._preview.configure(state="normal")
        self._preview.delete("1.0", "end")

        # Remove all dynamic colour tags
        for tag in self._preview.tag_names():
            if tag.startswith("dyn_color_"):
                self._preview.tag_delete(tag)

        # Parse line by line for block-level, then inline within each line
        lines = md.split("\n")
        for line in lines:
            h_match = re.match(r"^(#{1,6}) (.+)$", line)
            if h_match:
                level = len(h_match.group(1))
                text  = h_match.group(2) + "\n"
                self._preview.insert("end", text, f"h{level}")
                continue
            # Inline rendering
            self._render_inline(line + "\n")

        self._preview.configure(state="disabled")

    def _render_inline(self, line: str):
        """Insert a line with inline bold/italic/colour tags applied."""
        pattern = re.compile(
            r"(\*\*\*(.+?)\*\*\*)|(\*\*(.+?)\*\*)|(\*(.+?)\*)"
            r"|(\[color=([^\]]+)\](.+?)\[/color\])",
            re.DOTALL
        )
        pos = 0
        for m in pattern.finditer(line):
            # plain text before match
            if m.start() > pos:
                self._preview.insert("end", line[pos:m.start()])
            if m.group(1):   # bold italic
                self._preview.insert("end", m.group(2), "bold_italic")
            elif m.group(3): # bold
                self._preview.insert("end", m.group(4), "bold")
            elif m.group(5): # italic
                self._preview.insert("end", m.group(6), "italic")
            elif m.group(7): # color
                hex_col = m.group(8)
                tag_name = f"dyn_color_{hex_col.lstrip('#')}"
                if tag_name not in self._preview.tag_names():
                    self._preview.tag_configure(tag_name, foreground=hex_col)
                self._preview.insert("end", m.group(9), tag_name)
            pos = m.end()
        if pos < len(line):
            self._preview.insert("end", line[pos:])

    # ── Save ─────────────────────────────────────────────────────────────────
    def _save(self):
        subject = self._subject_var.get().strip()
        body    = self._text.get("1.0", "end-1c")
        save_draft(subject, body)
        messagebox.showinfo("Saved", "Draft saved successfully.", parent=self)
        self.destroy()

# Report Sending Tool

One-click Outlook email sender for supplier validation reports.  
Built with Python 3.11+, Tkinter (dark mode), and `pywin32` for Outlook COM automation.

---

## Features

| Feature | Description |
|---|---|
| **Browse & Refresh** | Select a root folder containing date-named subfolders (`YYYY-MM-DD HH-MM`). Automatically picks the most recent one and lists all `ValidationReport_*` files. |
| **Edit Draft** | Markdown-aware rich text editor with live preview. Supports bold, italic, headings (H1–H3), custom text colour, and font size. Subject line included. |
| **Contacts Manager** | Add, edit, and delete supplier contacts (Name / Company / Email). Multiple contacts per supplier are all included as To recipients. |
| **Save as Draft / Send Now** | Sends email via Outlook COM — either saves to Drafts or sends immediately. |
| **Auto Greeting** | Email body is automatically prepended with `Hi <Supplier> Team,` before sending. |
| **Per-supplier grouping** | Reports from the same supplier are combined into one email with all attachments. |
| **Persistent settings** | Folder path and send mode are saved to `config.json` and restored on next launch. |

---

## Project Structure

```
report-sending-tool/
├── main.py                        # Entry point
├── pyproject.toml                 # Poetry project & dependency config
├── poetry.toml                    # In-project venv config
├── contacts.json                  # Contact database (auto-created)
├── draft.json                     # Saved email draft (auto-created)
│
├── modules/
│   ├── contacts_manager.py        # Load/save/query contacts
│   ├── draft_manager.py           # Load/save email draft
│   ├── file_scanner.py            # Scan latest date folder, parse supplier names
│   └── outlook_sender.py         # Outlook COM: send or save-as-draft
│
└── ui/
    ├── main_window.py             # Main application window
    ├── contacts_window.py         # Contacts manager window (CRUD)
    └── draft_window.py            # Draft editor (Markdown + live preview)
```

---

## Requirements

- **Windows** with Microsoft Outlook installed and signed in
- **Python 3.11+**
- **Poetry 2.x** — [install guide](https://python-poetry.org/docs/#installation)

---

## Setup & Run

```powershell
# 1. Clone the repo
git clone https://github.com/max84517/report-sending-tool.git
cd report-sending-tool

# 2. Install dependencies (creates .venv inside the project folder)
poetry install

# 3. Run
poetry run python main.py
```

---

## File Name Convention

Reports inside the date folder must follow this pattern:

```
ValidationReport_<SupplierName>_<anything>.<ext>
```

Examples:
- `ValidationReport_Acrox_FY26_03.xlsx`
- `ValidationReport_Chicony_FY26_03.xlsx`

The middle segment (`Acrox`, `Chicony`, …) is matched against the **Company** field in your contacts list. If no match is found the report is skipped.

---

## Email Draft Syntax

The body uses Markdown syntax. Supported:

| Syntax | Result |
|---|---|
| `**text**` | **Bold** |
| `*text*` | *Italic* |
| `***text***` | ***Bold Italic*** |
| `# Heading` | H1 (also H2 `##`, H3 `###`) |
| `[color=#ff0000]text[/color]` | Coloured text |

The placeholder `{name}` is **not** used — the greeting `Hi <Supplier> Team,` is inserted automatically.

---

## Dependencies

| Package | Purpose |
|---|---|
| `pywin32` | Outlook COM automation (send / save draft) |
| `tkinter` | UI (stdlib, no install needed) |

---

## License

MIT

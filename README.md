# Report Sending Tool

One-click Outlook email sender for supplier validation reports.  
Built with Python 3.11+, Tkinter (dark mode), and `pywin32` for Outlook COM automation.

---

## Download

> **No Python required** — download the pre-built Windows executable:

**[⬇ Download ReportSendingTool-v1.0.0-win64.zip](https://github.com/max84517/report-sending-tool/releases/tag/v1.0.0)**

Extract the zip and run `ReportSendingTool.exe`. Keep all files in the same folder.

---

## Features

| Feature | Description |
|---|---|
| **Browse & Refresh** | Select a root folder containing date-named subfolders (`YYYY-MM-DD HH-MM`). Automatically picks the most recent one and lists all `ValidationReport_*` files. |
| **Edit Draft** | Markdown-aware rich text editor with live preview. Supports bold, italic, headings (H1–H3), custom text colour, and font size. Subject and body are saved persistently. |
| **Contacts Manager** | Add, edit, and delete supplier contacts (Name / Company / Email). Multiple contacts per supplier are all included as To recipients in one email. |
| **Save as Draft / Send Now** | Sends email via Outlook COM — either saves to Drafts or sends immediately. |
| **Per-supplier grouping** | All reports for the same supplier are combined into one email with all attachments. |
| **Auto placeholders** | `{supplier}` → supplier name, `{name}` → your name (set in Settings). Auto-prepended to subject as `Validation Report - <Supplier>`. |
| **User Settings** | Set your name once — used as the email sign-off. Required before sending. |
| **Persistent settings** | Folder path, send mode, and user name are saved to `config.json` and restored on next launch. |

---

## Project Structure

```
report-sending-tool/
├── main.py                        # Entry point
├── pyproject.toml                 # Poetry project & dependency config
├── poetry.toml                    # In-project venv config
├── ReportSendingTool.spec         # PyInstaller build spec
├── contacts.json                  # Contact database (auto-created)
├── draft.json                     # Saved email draft (auto-created/reset if missing)
│
├── modules/
│   ├── contacts_manager.py        # Load/save/query contacts (supports multiple per supplier)
│   ├── draft_manager.py           # Load/save draft with default template fallback
│   ├── file_scanner.py            # Scan latest date folder, parse supplier names
│   └── outlook_sender.py         # Outlook COM: send or save-as-draft, multi-recipient
│
└── ui/
    ├── main_window.py             # Main application window
    ├── contacts_window.py         # Contacts manager window (CRUD)
    ├── draft_window.py            # Draft editor (Markdown + live preview)
    └── settings_window.py         # User settings (name)
```

---

## Requirements

- **Windows** with Microsoft Outlook installed and signed in
- **Python 3.11–3.14**
- **Poetry 2.x** — [install guide](https://python-poetry.org/docs/#installation)

---

## Setup & Run (from source)

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

## Build Exe

```powershell
poetry run pyinstaller ReportSendingTool.spec --distpath "C:\Temp\RST\dist" --workpath "C:\Temp\RST\build" --noconfirm
```

Output: `C:\Temp\RST\dist\ReportSendingTool\ReportSendingTool.exe`

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

## Email Draft Placeholders

| Placeholder | Replaced with |
|---|---|
| `{supplier}` | Supplier name (from file name) |
| `{name}` | Your name (set in ⚙ Settings) |

Both work in the **Subject** and **Body**. The subject is automatically prefixed with `Validation Report - {supplier}`.

---

## Draft Markdown Syntax

| Syntax | Result |
|---|---|
| `**text**` | **Bold** |
| `*text*` | *Italic* |
| `***text***` | ***Bold Italic*** |
| `# Heading` | H1 (also `##` H2, `###` H3) |
| `[color=#ff0000]text[/color]` | Coloured text |

---

## Dependencies

| Package | Purpose |
|---|---|
| `pywin32` | Outlook COM automation (send / save draft) |
| `tkinter` | UI (stdlib, no install needed) |
| `pyinstaller` *(dev)* | Build standalone Windows exe |

---

## License

MIT


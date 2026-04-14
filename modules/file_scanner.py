import os
import re


def get_latest_folder(base_path: str) -> str | None:
    """Return the most recent date-named subfolder (e.g. '2026-04-12 11-38')."""
    if not os.path.isdir(base_path):
        return None
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}-\d{2}$")
    folders = [
        d for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and pattern.match(d)
    ]
    if not folders:
        return None
    folders.sort(reverse=True)
    return os.path.join(base_path, folders[0])


def scan_reports(base_path: str) -> list[dict]:
    """
    Scan the latest date folder and return a list of report dicts:
      { "filename": str, "supplier": str, "filepath": str }
    File name pattern: ValidationReport_<Supplier>_<rest>.<ext>
    """
    folder = get_latest_folder(base_path)
    if not folder:
        return []

    results = []
    pattern = re.compile(r"^ValidationReport_([^_]+)_(.+)$", re.IGNORECASE)
    for fname in sorted(os.listdir(folder)):
        fpath = os.path.join(folder, fname)
        if not os.path.isfile(fpath):
            continue
        name_no_ext = os.path.splitext(fname)[0]
        m = pattern.match(name_no_ext)
        if m:
            supplier = m.group(1)
            results.append({
                "filename": fname,
                "supplier": supplier,
                "filepath": fpath,
            })
    return results

import json
import os

DRAFT_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "draft.json")

DEFAULT_SUBJECT = "Validation Report - {supplier}"

DEFAULT_BODY = """Dear {supplier} Team,

Please find attached the Price Validation Report. Kindly review the flagged items and update the prices in both your **Supplier Shipment file** and **Master Price Table** accordingly.

---

**Report Comment Types**

The report may contain the following types of comments:

- **No mismatches found for this month.** \u2014 The rebate price in the Supplier Shipment file matches the Master Price Table. No action required.

- **Price Mismatch** \u2014 The rebate price in the Supplier Shipment file differs from the Master Price Table. Please align both files to the correct agreed price.

- **Exists in Master Table only** \u2014 The line item is present in the Master Price Table but missing from your Supplier Shipment file. Please verify whether this item should be included.

- **Exists in Supplier Shipment only** \u2014 The line item is present in your Supplier Shipment file but cannot be found in the Master Price Table. Please refer to the section below.

---

**Regarding "Exists in Supplier Shipment only"**

Our system matches records between the two files using a combined key of:

> **ODM Part#** + **ODM Site**

If either field does not match **exactly**, the record will be treated as unmatched and flagged as missing from the Master Price Table \u2014 even if the item exists under a slightly different format.

Common causes include:
- Differences in spacing, special characters, or trailing characters in the **ODM Part#**
- Inconsistent site name notation in **ODM Site** (e.g. `INVENTEC_CQ` vs `INVENTEC CQ`)

Please carefully cross-check these two fields in your Supplier Shipment file against the Master Price Table and ensure they are fully aligned.

---

If any of the flagged items represent a special case or exception, please let us know so we can handle them accordingly.

Best regards,
{name}"""


def load_draft() -> dict:
    if not os.path.exists(DRAFT_FILE):
        # Re-create file with defaults so it persists for next time
        save_draft(DEFAULT_SUBJECT, DEFAULT_BODY)
        return {"subject": DEFAULT_SUBJECT, "body": DEFAULT_BODY}
    try:
        with open(DRAFT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # File is corrupted — reset to defaults
        save_draft(DEFAULT_SUBJECT, DEFAULT_BODY)
        return {"subject": DEFAULT_SUBJECT, "body": DEFAULT_BODY}


def save_draft(subject: str, body: str) -> None:
    with open(DRAFT_FILE, "w", encoding="utf-8") as f:
        json.dump({"subject": subject, "body": body}, f, indent=2, ensure_ascii=False)

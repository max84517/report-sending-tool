import json
import os

CONTACTS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "contacts.json")


def load_contacts() -> list[dict]:
    if not os.path.exists(CONTACTS_FILE):
        return []
    with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_contacts(contacts: list[dict]) -> None:
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2, ensure_ascii=False)


def find_contact_by_supplier(supplier_name: str) -> dict | None:
    """Find the first contact where company matches supplier_name (case-insensitive)."""
    results = find_contacts_by_supplier(supplier_name)
    return results[0] if results else None


def find_contacts_by_supplier(supplier_name: str) -> list[dict]:
    """Return ALL contacts whose company matches supplier_name (case-insensitive)."""
    contacts = load_contacts()
    supplier_lower = supplier_name.lower()
    return [c for c in contacts if c.get("company", "").lower() == supplier_lower]

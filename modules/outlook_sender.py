"""
Outlook sender using win32com.client (pywin32).
Requires: pip install pywin32
"""
import re
import win32com.client  # type: ignore


def _md_to_html(md_text: str) -> str:
    """
    Minimal Markdown → HTML converter for email body.
    Supports: **bold**, *italic*, # headings, colour spans (custom <color:red>text</color>),
    and newlines → <br>.
    """
    text = md_text

    # Headings
    text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
    text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
    text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

    # Bold + italic
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<b><i>\1</i></b>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)

    # Custom colour tag: [color=#ff0000]text[/color]
    text = re.sub(
        r"\[color=([^\]]+)\](.+?)\[/color\]",
        r'<span style="color:\1">\2</span>',
        text,
        flags=re.DOTALL,
    )

    # Newlines
    text = text.replace("\n", "<br>")

    return f"<html><body>{text}</body></html>"


def send_email(
    to_addresses: list[str],
    subject: str,
    body_md: str,
    attachment_paths: list[str],
    save_as_draft: bool = False,
) -> None:
    """
    Send (or save as draft) one email via Outlook.

    Parameters
    ----------
    to_addresses     : list of recipient email addresses (all go in the To field)
    subject          : email subject
    body_md          : markdown body text
    attachment_paths : list of full paths to attach
    save_as_draft    : if True, save to Drafts; if False, send immediately
    """
    outlook = win32com.client.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)  # 0 = olMailItem

    mail.To = "; ".join(to_addresses)
    mail.Subject = subject
    mail.HTMLBody = _md_to_html(body_md)
    for path in attachment_paths:
        mail.Attachments.Add(path)

    if save_as_draft:
        mail.Save()
    else:
        mail.Send()

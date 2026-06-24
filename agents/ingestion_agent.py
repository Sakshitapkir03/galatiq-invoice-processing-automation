import json
import re
from models.schemas import InvoiceData, InvoiceItem
from tools.file_reader import read_invoice


KNOWN_ITEMS = [
    "WidgetA",
    "WidgetB",
    "GadgetX",
    "FakeItem",
    "SuperGizmo",
    "MegaSprocket",
    "WidgetC",
]


def extract_invoice_id(text: str):
    match = re.search(r"INV-\d+", text, re.IGNORECASE)
    return match.group(0).upper() if match else None


def extract_vendor(text: str):
    match = re.search(r"Vendor:\s*(.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_due_date(text: str):
    match = re.search(r"Due Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def extract_amount(text: str):
    patterns = [
        r"Total Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"Total:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1).replace(",", ""))

    return None


def extract_items(text: str):
    items = []

    for item_name in KNOWN_ITEMS:
        pattern = rf"{item_name}\s+qty:\s*(-?\d+)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            items.append(
                InvoiceItem(
                    name=item_name,
                    quantity=int(match.group(1)),
                )
            )

    return items


def parse_json_invoice(text: str):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    items = []

    for item in data.get("items", []):
        name = item.get("name") or item.get("item")
        quantity = item.get("quantity") or item.get("qty")

        if name and quantity is not None:
            items.append(InvoiceItem(name=name, quantity=int(quantity)))

    return InvoiceData(
        invoice_id=data.get("invoice_id") or data.get("invoice_number"),
        vendor=data.get("vendor"),
        amount=float(data["amount"]) if data.get("amount") is not None else None,
        due_date=data.get("due_date"),
        items=items,
        raw_text=text,
    )


def ingestion_agent(state):
    logs = state.get("logs", [])
    invoice_path = state["invoice_path"]

    raw_text = read_invoice(invoice_path)

    invoice = parse_json_invoice(raw_text)

    if invoice is None:
        invoice = InvoiceData(
            invoice_id=extract_invoice_id(raw_text),
            vendor=extract_vendor(raw_text),
            amount=extract_amount(raw_text),
            due_date=extract_due_date(raw_text),
            items=extract_items(raw_text),
            raw_text=raw_text,
        )

    logs.append("[INGESTION] Extracted invoice data")

    return {
        **state,
        "invoice": invoice,
        "logs": logs,
    }
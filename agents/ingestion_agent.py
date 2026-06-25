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


def clean_money(value):
    if value is None:
        return None
    return float(str(value).replace("$", "").replace(",", "").strip())


def extract_invoice_id(text: str):
    patterns = [
        r"INV-\d+",
        r"Inv #:\s*(\d+)",
        r"invoice_number,([A-Za-z0-9-]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1) if match.groups() else match.group(0)
            return value if value.upper().startswith("INV-") else f"INV-{value}"

    return None


def extract_vendor(text: str):
    patterns = [
        r"Vendor:\s*(.+)",
        r"Vndr:\s*(.+)",
        r"Supplier:\s*(.+)",
        r"vendor,([^\n]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_due_date(text: str):
    patterns = [
        r"Due Date:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
        r"Due Dt:\s*([0-9]{4}-[0-9]{2}-[0-9]{2})",
        r"due_date,([0-9]{4}-[0-9]{2}-[0-9]{2})",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_amount(text: str):
    patterns = [
        r"Total Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"Total:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"Amount:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"Amt:\s*\$?([\d,]+(?:\.\d{2})?)",
        r"total,([\d,]+(?:\.\d{2})?)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return clean_money(match.group(1))

    return None


def extract_items(text: str):
    items = []

    for item_name in KNOWN_ITEMS:
        patterns = [
            rf"{item_name}\s+qty:\s*(-?\d+)",
            rf"{item_name}\s+qty\s+(-?\d+)",
            rf"{item_name}\s+(-?\d+)\s+\$",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                items.append(InvoiceItem(name=item_name, quantity=int(match.group(1))))
                break

    if items:
        return items

    csv_items = []
    lines = [line.strip() for line in text.splitlines()]
    current_item = None

    for line in lines:
        if line.lower().startswith("item,"):
            current_item = line.split(",", 1)[1].strip()

        elif line.lower().startswith("quantity,") and current_item:
            quantity = int(line.split(",", 1)[1].strip())
            csv_items.append(InvoiceItem(name=current_item, quantity=quantity))
            current_item = None

    return csv_items


def parse_json_invoice(text: str):
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    vendor = data.get("vendor")
    if isinstance(vendor, dict):
        vendor = vendor.get("name")

    amount = (
        data.get("amount")
        or data.get("total")
        or data.get("total_amount")
    )

    items = []
    for item in data.get("items", data.get("line_items", [])):
        name = item.get("name") or item.get("item")
        quantity = item.get("quantity") or item.get("qty")

        if name and quantity is not None:
            items.append(InvoiceItem(name=name, quantity=int(quantity)))

    return InvoiceData(
        invoice_id=data.get("invoice_id") or data.get("invoice_number"),
        vendor=vendor,
        amount=clean_money(amount),
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
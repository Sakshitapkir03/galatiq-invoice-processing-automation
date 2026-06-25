from graph.workflow import build_invoice_workflow
from setup_inventory import setup_inventory


def run_invoice(path):
    setup_inventory()
    workflow = build_invoice_workflow()
    return workflow.invoke({"invoice_path": path, "logs": []})


def test_valid_text_invoice_is_paid():
    result = run_invoice("data/invoices/invoice_1001.txt")

    assert result["validation"].is_valid is True
    assert result["approval"].decision == "APPROVED"
    assert result["payment"].status == "PAID"


def test_stock_mismatch_invoice_is_rejected():
    result = run_invoice("data/invoices/invoice_1002.txt")

    assert result["validation"].is_valid is False
    assert result["approval"].decision == "REJECTED"
    assert result["payment"].status == "NOT_PAID"


def test_json_invoice_is_paid():
    result = run_invoice("data/invoices/invoice_1004.json")

    assert result["invoice"].vendor == "Precision Parts Ltd."
    assert result["payment"].status == "PAID"


def test_csv_invoice_is_paid():
    result = run_invoice("data/invoices/invoice_1006.csv")

    assert result["invoice"].vendor == "Acme Industrial Supplies"
    assert result["payment"].status == "PAID"


def test_pdf_invoice_is_paid():
    result = run_invoice("data/invoices/invoice_1011.pdf")

    assert result["invoice"].vendor == "Summit Manufacturing Co."
    assert result["payment"].status == "PAID"
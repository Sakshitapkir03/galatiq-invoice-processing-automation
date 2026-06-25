import argparse
import json
import warnings

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from graph.workflow import build_invoice_workflow


warnings.filterwarnings("ignore")
load_dotenv()

console = Console()


def to_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def print_invoice(invoice):
    table = Table(show_header=False)
    table.add_column("Field")
    table.add_column("Value")

    table.add_row("Invoice ID", invoice.invoice_id or "Missing")
    table.add_row("Vendor", invoice.vendor or "Missing")
    table.add_row("Amount", f"${invoice.amount:,.2f}" if invoice.amount else "Missing")
    table.add_row("Due Date", invoice.due_date or "Missing")

    items = ", ".join([f"{item.name} x {item.quantity}" for item in invoice.items]) or "Missing"
    table.add_row("Items", items)

    console.print(Panel(table, title="Invoice"))


def print_result(result):
    invoice = result["invoice"]
    validation = result["validation"]
    approval = result["approval"]
    payment = result["payment"]

    print_invoice(invoice)

    validation_status = "PASSED" if validation.is_valid else "FAILED"
    validation_details = "No validation issues found."

    if validation.issues:
        validation_details = "\n".join([f"- {issue.message}" for issue in validation.issues])

    console.print(Panel(validation_details, title=f"Validation: {validation_status}"))

    approval_text = (
        f"Decision: {approval.decision}\n"
        f"Reason: {approval.reason}\n"
        f"Reflection: {approval.reflection}"
    )
    console.print(Panel(approval_text, title="Approval Review"))

    payment_text = json.dumps(to_dict(payment), indent=2)
    console.print(Panel(payment_text, title=f"Payment: {payment.status}"))

    console.print(f"\nFinal Status: {payment.status}")


def main():
    parser = argparse.ArgumentParser(description="Invoice processing automation for Acme Corp")
    parser.add_argument("--invoice_path", required=True, help="Path to the invoice file")
    args = parser.parse_args()

    workflow = build_invoice_workflow()
    result = workflow.invoke({"invoice_path": args.invoice_path, "logs": []})

    print_result(result)


if __name__ == "__main__":
    main()
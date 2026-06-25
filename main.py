from dotenv import load_dotenv

load_dotenv()
import argparse
import json

from graph.workflow import build_invoice_workflow


def to_dict(value):
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value


def main():
    parser = argparse.ArgumentParser(description="Invoice processing automation for Acme Corp")
    parser.add_argument("--invoice_path", required=True, help="Path to the invoice file")
    args = parser.parse_args()

    workflow = build_invoice_workflow()

    result = workflow.invoke({
        "invoice_path": args.invoice_path,
        "logs": [],
    })

    print("\n=== Logs ===")
    for log in result.get("logs", []):
        print(log)

    print("\n=== Invoice ===")
    print(json.dumps(to_dict(result["invoice"]), indent=2))

    print("\n=== Validation ===")
    print(json.dumps(to_dict(result["validation"]), indent=2))

    print("\n=== Approval ===")
    print(json.dumps(to_dict(result["approval"]), indent=2))

    print("\n=== Payment ===")
    print(json.dumps(to_dict(result["payment"]), indent=2))

    print("\n=== Final Status ===")
    print(result["payment"].status)


if __name__ == "__main__":
    main()
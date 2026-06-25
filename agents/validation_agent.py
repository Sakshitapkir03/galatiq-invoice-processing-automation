from models.schemas import ValidationResult, ValidationIssue
from tools.inventory_tool import get_stock


def validation_agent(state):
    logs = state.get("logs", [])
    invoice = state["invoice"]
    issues = []

    if not invoice.vendor:
        issues.append(ValidationIssue(field="vendor", message="Vendor is missing"))

    if invoice.amount is None:
        issues.append(ValidationIssue(field="amount", message="Amount is missing"))
    elif invoice.amount <= 0:
        issues.append(ValidationIssue(field="amount", message="Amount must be positive"))

    if not invoice.due_date:
        issues.append(ValidationIssue(field="due_date", message="Due date is missing"))

    if not invoice.items:
        issues.append(ValidationIssue(field="items", message="No items were extracted from the invoice"))

    for item in invoice.items:
        stock = get_stock(item.name)

        if item.quantity <= 0:
            issues.append(
                ValidationIssue(
                    field="items",
                    message=f"{item.name} has invalid quantity {item.quantity}",
                )
            )
        elif stock is None:
            issues.append(
                ValidationIssue(
                    field="items",
                    message=f"{item.name} was not found in inventory",
                )
            )
        elif stock == 0:
            issues.append(
                ValidationIssue(
                    field="items",
                    message=f"{item.name} has zero stock and should be reviewed",
                )
            )
        elif item.quantity > stock:
            issues.append(
                ValidationIssue(
                    field="items",
                    message=f"{item.name} requested quantity {item.quantity} exceeds available stock {stock}",
                )
            )

    result = ValidationResult(
        is_valid=len(issues) == 0,
        issues=issues,
    )

    logs.append("[VALIDATION] Passed" if result.is_valid else "[VALIDATION] Failed")

    return {
        **state,
        "validation": result,
        "logs": logs,
    }
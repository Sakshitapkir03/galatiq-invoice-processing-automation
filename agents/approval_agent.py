from models.schemas import ApprovalDecision


APPROVAL_THRESHOLD = 10000


def reflect_on_decision(invoice, validation, decision, reason):
    if decision == "REJECTED":
        return "The rejection is appropriate because unresolved validation issues could lead to payment errors."

    if invoice.amount and invoice.amount > APPROVAL_THRESHOLD:
        return "The approval is reasonable only because validation passed, but the high amount should be visible for VP-level review."

    return "The approval is reasonable because required fields are present and validation passed."


def approval_agent(state):
    logs = state.get("logs", [])
    invoice = state["invoice"]
    validation = state["validation"]

    if not validation.is_valid:
        issue_text = "; ".join(issue.message for issue in validation.issues)

        decision = "REJECTED"
        reason = f"Invoice failed validation: {issue_text}"

    elif invoice.amount and invoice.amount > APPROVAL_THRESHOLD:
        decision = "APPROVED"
        reason = "Invoice passed validation but exceeds $10,000, so it requires additional VP-level scrutiny."

    else:
        decision = "APPROVED"
        reason = "Invoice passed validation and is within the standard approval threshold."

    reflection = reflect_on_decision(invoice, validation, decision, reason)

    approval = ApprovalDecision(
        decision=decision,
        reason=reason,
        reflection=reflection,
    )

    logs.append(f"[APPROVAL] {decision}")

    return {
        **state,
        "approval": approval,
        "logs": logs,
    }
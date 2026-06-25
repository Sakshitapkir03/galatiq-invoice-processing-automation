from models.schemas import PaymentResult
from tools.payment_tool import mock_payment


def payment_agent(state):
    logs = state.get("logs", [])
    invoice = state["invoice"]
    approval = state["approval"]

    if approval.decision == "APPROVED":
        payment_response = mock_payment(invoice.vendor, invoice.amount)

        payment = PaymentResult(
            status="PAID",
            details=payment_response,
        )

        logs.append("[PAYMENT] Payment processed")

    else:
        payment = PaymentResult(
            status="NOT_PAID",
            details={
                "reason": approval.reason,
            },
        )

        logs.append("[PAYMENT] Payment skipped because invoice was rejected")

    return {
        **state,
        "payment": payment,
        "logs": logs,
    }
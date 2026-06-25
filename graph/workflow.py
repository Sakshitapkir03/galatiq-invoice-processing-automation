from langgraph.graph import StateGraph, END

from models.schemas import InvoiceState
from agents.ingestion_agent import ingestion_agent
from agents.validation_agent import validation_agent
from agents.approval_agent import approval_agent
from agents.payment_agent import payment_agent


def build_invoice_workflow():
    workflow = StateGraph(InvoiceState)

    workflow.add_node("ingestion", ingestion_agent)
    workflow.add_node("validation", validation_agent)
    workflow.add_node("approval", approval_agent)
    workflow.add_node("payment", payment_agent)

    workflow.set_entry_point("ingestion")

    workflow.add_edge("ingestion", "validation")
    workflow.add_edge("validation", "approval")
    workflow.add_edge("approval", "payment")
    workflow.add_edge("payment", END)

    return workflow.compile()
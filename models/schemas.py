from typing import List, Optional, Dict, Any, TypedDict
from pydantic import BaseModel, Field


class InvoiceItem(BaseModel):
    name: str
    quantity: int


class InvoiceData(BaseModel):
    invoice_id: Optional[str] = None
    vendor: Optional[str] = None
    amount: Optional[float] = None
    items: List[InvoiceItem] = Field(default_factory=list)
    due_date: Optional[str] = None
    raw_text: Optional[str] = None


class ValidationIssue(BaseModel):
    field: str
    message: str
    severity: str = "error"


class ValidationResult(BaseModel):
    is_valid: bool
    issues: List[ValidationIssue] = Field(default_factory=list)


class ApprovalDecision(BaseModel):
    decision: str
    reason: str
    reflection: str


class PaymentResult(BaseModel):
    status: str
    details: Dict[str, Any]


class InvoiceState(TypedDict, total=False):
    invoice_path: str
    invoice: InvoiceData
    validation: ValidationResult
    approval: ApprovalDecision
    payment: PaymentResult
    logs: List[str]
import json
import os
from openai import OpenAI, OpenAIError


MODEL_NAME = "grok-4.3"
XAI_BASE_URL = "https://api.x.ai/v1"


def local_review(invoice, validation, draft_decision):
    if not validation.is_valid:
        return {
            "decision": draft_decision,
            "reflection": "Rejected after review because validation found issues that should block payment.",
        }

    if invoice.amount and invoice.amount > 10000:
        return {
            "decision": draft_decision,
            "reflection": "Approved after review, but flagged for VP-level scrutiny because the amount is above 10000.",
        }

    return {
        "decision": draft_decision,
        "reflection": "Approved after review because validation passed and the amount is within the standard threshold.",
    }


def review_approval(invoice, validation, draft_decision, draft_reason):
    api_key = os.getenv("XAI_API_KEY")

    if not api_key:
        return local_review(invoice, validation, draft_decision)

    client = OpenAI(api_key=api_key, base_url=XAI_BASE_URL)

    payload = {
        "invoice": invoice.model_dump(),
        "validation": validation.model_dump(),
        "draft_decision": draft_decision,
        "draft_reason": draft_reason,
        "business_rules": [
            "Reject invoices with validation issues.",
            "Invoices above 10000 require VP-level scrutiny.",
            "Only approved invoices should continue to payment.",
        ],
    }

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are reviewing an invoice approval decision. "
                        "Return only valid JSON with keys: decision and reflection. "
                        "Decision must be APPROVED or REJECTED."
                    ),
                },
                {"role": "user", "content": json.dumps(payload)},
            ],
        )

        content = response.choices[0].message.content.strip()
        parsed = json.loads(content)

        return {
            "decision": parsed.get("decision", draft_decision),
            "reflection": parsed.get("reflection", content),
        }

    except (OpenAIError, json.JSONDecodeError, KeyError, TypeError) as error:
        fallback = local_review(invoice, validation, draft_decision)
        fallback["reflection"] = f"{fallback['reflection']} Grok review was unavailable, so local review was used."
        return fallback
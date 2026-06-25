Invoice Processing Automation

Project Overview

This project implements an end-to-end invoice processing workflow for Acme Corp using a multi-agent architecture built with LangGraph. The workflow ingests invoices from multiple file formats, extracts structured information, validates invoice data against a local SQLite inventory database, performs an approval decision with a review step, and finally executes a mock payment for approved invoices.

The implementation follows the assessment requirements while keeping the workflow deterministic wherever possible and using an LLM only where reasoning adds value. The goal was to build a working prototype that is reliable, testable, and easy to extend.

⸻

Requirements Mapping

Assessment Requirement	Implementation
Multi-agent workflow	LangGraph StateGraph
Invoice ingestion	TXT, PDF, CSV and JSON
Structured extraction	Pydantic models
Inventory validation	SQLite database
Approval reasoning	Rule-based approval with reflection and optional Grok review
Payment	Mock payment function
Local execution	Python CLI
Automated tests	pytest

⸻

Architecture

Invoice
    │
    ▼
Ingestion Agent
    │
    ▼
Validation Agent
    │
    ▼
Approval Agent
    │
    ▼
Payment Agent

Ingestion Agent

* Reads invoice files
* Supports TXT, PDF, JSON and CSV
* Extracts structured invoice information
* Produces a shared workflow state

Validation Agent

* Validates required fields
* Checks inventory using SQLite
* Detects unknown items
* Detects insufficient stock
* Detects invalid quantities

Approval Agent

* Applies business approval rules
* Reviews validation results
* Produces approval or rejection
* Performs a reflection step
* Uses Grok when configured and gracefully falls back to local reasoning if unavailable

Payment Agent

* Executes the provided mock payment function
* Records payment status
* Logs rejected invoices

⸻

Project Structure

agents/
    ingestion_agent.py
    validation_agent.py
    approval_agent.py
    payment_agent.py
graph/
    workflow.py
models/
    invoice.py
tools/
    database.py
    file_reader.py
    grok_client.py
    payment.py
tests/
    test_workflow.py
data/
    invoices/
main.py
setup_inventory.py

⸻

Workflow

I implemented the workflow incrementally rather than attempting to build the complete system at once.

1. Read invoice files from disk.
2. Verified that extraction worked correctly.
3. Added validation against the inventory database.
4. Implemented approval logic.
5. Connected the payment stage.
6. Added automated tests after the end-to-end workflow was stable.
7. Improved the command-line output for easier inspection of results.

Building the system in small, verifiable stages made debugging significantly easier and ensured every component worked correctly before introducing the next one.

⸻

Engineering Decisions

Why LangGraph?

The assessment requested a multi-agent implementation, and LangGraph provided a natural way to model the invoice lifecycle as a state-driven workflow. Each agent performs a single responsibility while operating on a shared workflow state, making the execution path easy to understand and debug.

Since invoice processing follows a predictable business process, a state graph was a good fit for representing the sequence of ingestion, validation, approval, and payment.

⸻

Why deterministic extraction?

Invoice fields such as vendor name, invoice number, due date and line items follow predictable formats. I intentionally used deterministic parsing with regular expressions and structured processing rather than relying entirely on an LLM.

This approach provides consistent outputs, reduces unnecessary model calls, and makes extraction easier to test.

The LLM is reserved for the stage where reasoning is actually beneficial.

⸻

Why SQLite?

The assessment requires validating invoices against an inventory database.

SQLite provided a lightweight local database that required no external services while still allowing realistic inventory validation. Keeping the database local also makes the project simple to run on any machine.

⸻

Why use the LLM only during approval?

I intentionally limited LLM usage to the approval stage.

Extraction, validation and inventory checks should always produce deterministic results for identical inputs. Business rules such as stock validation should not depend on probabilistic model outputs.

Approval reasoning, however, benefits from natural language explanations and reflection, making it the most appropriate place to integrate Grok.

⸻

Why include a Grok fallback?

The approval agent supports Grok whenever an API key is available.

If the API is unavailable or credentials are missing, the workflow automatically performs a local review instead of failing. This keeps the prototype fully executable while still supporting LLM-based reasoning when configured.

⸻

Testing Strategy

Rather than waiting until the end of development, I verified each stage before moving to the next.

Once the complete workflow was assembled, I added automated tests covering:

* Successful invoice processing
* Validation failures
* Approval decisions
* Payment execution
* End-to-end workflow execution

This made it easier to catch regressions while continuing development.

⸻

Running the Project

Install dependencies

pip install -r requirements.txt

Create the inventory database

python setup_inventory.py

(Optional) Configure Grok

XAI_API_KEY=your_api_key

Run the workflow

python main.py --invoice_path=data/invoices/invoice_1001.txt

⸻

Running Tests

pytest

Current test suite:

* End-to-end workflow
* Successful approval
* Validation failure
* Payment execution
* Inventory validation

⸻

Sample Results

Approved Invoice

* Invoice extracted successfully
* Inventory validation passed
* Approval granted
* Mock payment executed

Rejected Invoice

* Inventory validation failed
* Approval rejected
* Payment skipped
* Rejection reason logged

⸻

Future Improvements

If this prototype were extended further, the next improvements would include:

* OCR support for scanned invoices
* Human approval queue for flagged invoices
* Integration with a real payment provider
* Additional business validation rules
* Retry and recovery logic for failed processing
* Persistent workflow history and audit logs

⸻

Development Notes

The focus of this implementation was to first build a reliable end-to-end workflow before expanding functionality.

I began with a minimal pipeline capable of processing a single invoice successfully. Once that workflow was stable, I incrementally added support for additional file formats, inventory validation, approval reasoning, payment execution, automated testing, and improved command-line output.

This incremental approach made it easier to validate each component independently and helped maintain a stable working system throughout development.
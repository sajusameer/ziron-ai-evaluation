# Freight Document Parser & Validation System

An AI-powered Python application that extracts structured data from unstructured freight documents and validates the extracted information against deterministic business rules.

## Overview

Freight documents often contain important information in an unstructured format. This project uses an LLM to convert the raw document text into a strict typed JSON structure and then applies deterministic Python validation rules.

The workflow is:

```text
Raw Freight Document
        ↓
LLM Extraction
        ↓
Pydantic Schema Validation
        ↓
Business Rule Validation
        ↓
Decision
   ┌────┴────┐
   ↓         ↓
APPROVED   FLAGGED_FOR_HUMAN_REVIEW
```

## Features

* Extracts freight information from unstructured text using an LLM
* Enforces a strict JSON structure using Pydantic
* Validates financial calculations
* Detects overweight loads
* Detects missing required information
* Separates LLM extraction from deterministic business validation
* Provides automated tests for validation and end-to-end workflow
* Uses environment variables for API credentials

## Tech Stack

* Python 3.10+
* Pydantic 2
* OpenAI Python SDK
* Groq API
* `openai/gpt-oss-20b`
* python-dotenv
* Pytest-style test functions

## Project Structure

```text
ziron-ai-evaluation/
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── parser.py
│   └── validator.py
│
├── data/
│   └── sample.txt
│
├── .env
├── .gitignore
├── main.py
├── test_models.py
├── test_validator.py
├── test_workflow.py
└── README.md
```

## Data Model

The extracted freight document contains:

```json
{
  "carrier_name": "string",
  "load_number": "string",
  "pickup_location": {
    "city": "string",
    "state": "string",
    "zip": "string"
  },
  "delivery_location": {
    "city": "string",
    "state": "string",
    "zip": "string"
  },
  "total_linehaul_rate": 0,
  "fuel_surcharge": 0,
  "total_pay": 0,
  "weight_lbs": 0
}
```

Pydantic validates the LLM output before the business rules are executed.

## Validation Rules

### 1. Rate Mismatch

The expected total is calculated as:

```text
total_linehaul_rate + fuel_surcharge
```

If the calculated value does not equal `total_pay`:

```text
RATE_MISMATCH
```

is added as an error.

### 2. Overweight Load

If:

```text
weight_lbs > 45,000
```

the system generates:

```text
OVERWEIGHT_LOAD
```

as a warning.

### 3. Incomplete Data

Required load and location information must be present.

Missing required information produces:

```text
INCOMPLETE_DATA
```

as an error.

## Decision Logic

If no validation issues are detected:

```json
{
  "status": "APPROVED"
}
```

If validation issues are detected:

```json
{
  "status": "FLAGGED_FOR_HUMAN_REVIEW"
}
```

The flagged response also contains the detected reasons.

## Setup

### 1. Create a virtual environment

```powershell
python -m venv .venv
```

### 2. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the API key

Create a `.env` file in the project root:

```text
GROQ_API_KEY=your_api_key_here
```

Do not commit the `.env` file to Git.

## Running the Application

Run the sample freight document:

```powershell
python main.py data/sample.txt
```

The application will:

1. Read the raw freight document.
2. Send the document to the LLM.
3. Extract structured JSON.
4. Validate the JSON using Pydantic.
5. Run deterministic business rules.
6. Return the final decision.

## Running Tests

Run the validation tests:

```powershell
python test_validator.py
```

Run the end-to-end workflow test:

```powershell
python test_workflow.py
```

## Sample Result

The provided sample document contains:

```text
Linehaul Rate: $2,200
Fuel Surcharge: $350
Total Agreed Amount: $2,800

Weight: 46,800 lbs
```

The calculated financial total is:

```text
$2,200 + $350 = $2,550
```

Since the document states `$2,800`, the system detects:

```text
RATE_MISMATCH
```

The weight is also greater than 45,000 lbs, so the system detects:

```text
OVERWEIGHT_LOAD
```

Therefore, the final decision is:

```text
FLAGGED_FOR_HUMAN_REVIEW
```

## Architecture and Scaling

The current implementation is intentionally modular:

```text
                ┌──────────────────┐
                │ Freight Document │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ LLM Parser       │
                │ parser.py        │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Pydantic Models  │
                │ models.py        │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Rule Validator   │
                │ validator.py     │
                └────────┬─────────┘
                         ↓
                ┌──────────────────┐
                │ Decision Layer   │
                │ main.py          │
                └──────────────────┘
```

### Scaling to 100,000 PDFs per day

For production-scale processing, the synchronous CLI workflow can be replaced with an asynchronous distributed architecture.

A possible architecture:

```text
PDF Upload
    ↓
Object Storage
    ↓
Message Queue
    ↓
PDF/Text Extraction Workers
    ↓
LLM Processing Workers
    ↓
Pydantic Validation
    ↓
Business Rule Engine
    ↓
Database
    ↓
Human Review Queue
```

Important scaling considerations:

* Use a queue-based architecture to distribute documents across workers.
* Run multiple workers in parallel.
* Use object storage for original PDFs.
* Add retry mechanisms with exponential backoff for temporary LLM/API failures.
* Use dead-letter queues for documents that repeatedly fail.
* Make processing idempotent to prevent duplicate processing.
* Apply provider rate limits and concurrency controls.
* Add structured logging and monitoring.
* Store processing status and validation results in a database.
* Add OCR for scanned PDFs.
* Autoscale workers based on queue depth.
* Avoid sending unnecessary repeated LLM requests by caching or deduplicating documents.
* Keep sensitive freight information out of application logs.

100,000 documents per day is approximately 1.16 documents per second on average. Production systems should be designed with additional capacity to handle traffic bursts rather than targeting only the average rate.

## Design Decisions

### LLM for Extraction

The LLM is responsible for understanding messy, unstructured freight documents and extracting the required fields.

### Pydantic for Schema Enforcement

Pydantic provides typed models and rejects malformed LLM output before it reaches the business logic.

### Python for Business Rules

Business rules are deterministic and should not depend on the LLM. This makes financial validation predictable, testable, and easier to maintain.

### Modular Architecture

Parsing and validation are separated so that either component can be changed independently.

## Security

* API credentials are stored in `.env`.
* `.env` is excluded from Git using `.gitignore`.
* Production systems should use a secure secret manager.
* Sensitive freight data should not be written to application logs.
* Access to stored documents should follow least-privilege principles.

## Current Status

The core workflow is implemented and tested:

* LLM extraction: implemented
* Strict Pydantic validation: implemented
* Rate validation: implemented
* Overweight validation: implemented
* Incomplete data validation: implemented
* End-to-end workflow: implemented
* Automated tests: implemented
* Scaling architecture: documented

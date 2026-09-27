# Freight Document Parser & Validation System

An AI-powered Python application that extracts structured data from unstructured freight documents, validates the extracted information against deterministic business rules, and executes an automated decision workflow.

## Overview

Freight documents such as rate confirmations, invoices, and shipping orders often contain important information in unstructured text.

This project uses an LLM to extract the required information into a strict typed JSON structure using Pydantic. After extraction, deterministic Python business rules validate the data and produce an automated decision.

The workflow is:

```text
Raw Freight Document
        |
        v
LLM Extraction
        |
        v
Pydantic Schema Validation
        |
        v
Business Rule Validation
        |
        v
Decision Workflow
        |
    +---+---+
    |       |
    v       v
APPROVED   FLAGGED_FOR_HUMAN_REVIEW
```

## Features

* Extracts freight information from unstructured documents using an LLM
* Enforces a typed JSON schema using Pydantic
* Validates financial calculations
* Detects overweight loads
* Detects missing required information
* Separates LLM extraction from deterministic business validation
* Provides automated validation and end-to-end tests
* Uses environment variables for API credentials
* Includes architecture and production scaling considerations

## Tech Stack

* Python 3.10+
* Pydantic 2
* OpenAI Python SDK
* Groq API
* `openai/gpt-oss-20b`
* python-dotenv

## Project Structure

```text
ziron-ai-evaluation/
|
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── parser.py
│   └── validator.py
|
├── data/
│   └── sample.txt
|
├── .env.example
├── .gitignore
├── ARCHITECTURE.md
├── README.md
├── main.py
├── requirements.txt
├── sample_output.json
├── test_models.py
├── test_validator.py
└── test_workflow.py
```

### File Responsibilities

| File                 | Purpose                                                             |
| -------------------- | ------------------------------------------------------------------- |
| `app/models.py`      | Defines Pydantic data models                                        |
| `app/parser.py`      | Sends the document to the LLM and validates the structured response |
| `app/validator.py`   | Implements deterministic business rules                             |
| `main.py`            | Executes the complete parsing, validation, and decision workflow    |
| `data/sample.txt`    | Sample raw freight document                                         |
| `sample_output.json` | Example output from the sample document                             |
| `test_models.py`     | Tests the data models                                               |
| `test_validator.py`  | Tests individual validation rules                                   |
| `test_workflow.py`   | Tests the end-to-end workflow                                       |
| `ARCHITECTURE.md`    | Production architecture and scaling notes                           |

## Data Schema

The extracted freight document must contain the following structure:

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

Pydantic validates the LLM response before the data reaches the business-rule validation layer.

## Document Parsing & Schema Enforcement

The LLM is instructed to:

* Extract only the required fields.
* Preserve financial values exactly as stated in the document.
* Avoid calculating or correcting financial values.
* Avoid inventing missing information.
* Return JSON matching the defined schema.

The resulting JSON is then validated using Pydantic's `model_validate_json()`.

This creates two levels of validation:

```text
LLM Structured JSON
        |
        v
Pydantic Validation
        |
        v
Typed FreightDocument
```

If the LLM returns malformed or invalid data, the application stops before business validation is executed.

## Validation Rules

### 1. Rate Mismatch

The expected total is:

```text
total_linehaul_rate + fuel_surcharge
```

If the calculated value does not equal `total_pay`, the system adds:

```text
RATE_MISMATCH
```

as an error.

### 2. Overweight Load

If:

```text
weight_lbs > 45,000
```

the system adds:

```text
OVERWEIGHT_LOAD
```

as a warning.

### 3. Incomplete Data

Required load and location information must be available.

If required information is missing, the system adds:

```text
INCOMPLETE_DATA
```

as an error.

## Decision Workflow

The validation engine returns two categories:

```text
errors
warnings
```

If there are no errors or warnings, the document is approved:

```json
{
  "status": "APPROVED",
  "data": {}
}
```

If validation identifies an error, the document is sent for human review:

```json
{
  "status": "FLAGGED_FOR_HUMAN_REVIEW",
  "flag_reasons": [],
  "data": {}
}
```

The sample document contains both a rate mismatch and an overweight warning, so it is flagged for human review.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/sajusameer/ziron-ai-evaluation.git
cd ziron-ai-evaluation
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure the API key

Create a `.env` file in the project root.

You can use `.env.example` as a template:

```text
GROQ_API_KEY=your_api_key_here
```

The actual `.env` file must not be committed to Git.

## Running the Application

Run the application against the provided sample document:

```powershell
python main.py data/sample.txt
```

The application will:

1. Read the raw freight document.
2. Send the document to the LLM.
3. Extract structured JSON.
4. Validate the JSON using Pydantic.
5. Run deterministic business rules.
6. Execute the decision workflow.
7. Print the final result.

## Running Tests

### Validation tests

```powershell
python test_validator.py
```

### End-to-end workflow test

```powershell
python test_workflow.py
```

### Model test

```powershell
python test_models.py
```

All tests should pass before submitting the project.

## Sample Document Result

The provided sample document contains:

```text
Linehaul Rate: $2,200.00
Fuel Surcharge: $350.00
Total Agreed Amount: $2,800.00
Total Weight: 46,800 lbs
```

The expected financial total is:

```text
$2,200 + $350 = $2,550
```

However, the document states:

```text
$2,800
```

Therefore:

```text
RATE_MISMATCH
```

is detected.

The document also contains:

```text
46,800 lbs
```

which is greater than the 45,000 lbs limit.

Therefore:

```text
OVERWEIGHT_LOAD
```

is also detected.

The final decision is:

```text
FLAGGED_FOR_HUMAN_REVIEW
```

A sample JSON result is included in:

```text
sample_output.json
```

## Architecture

The current implementation separates the main responsibilities into independent modules:

```text
                 +------------------+
                 | Freight Document |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 |   LLM Parser     |
                 |    parser.py     |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Pydantic Models  |
                 |    models.py     |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Rule Validator   |
                 |  validator.py    |
                 +--------+---------+
                          |
                          v
                 +------------------+
                 | Decision Layer   |
                 |     main.py      |
                 +------------------+
```

### Separation of Responsibilities

The LLM handles the unstructured language extraction problem.

Pydantic handles schema and type validation.

Python handles deterministic business rules.

The decision layer combines the validation results into the final workflow status.

This separation makes the system easier to test, debug, maintain, and scale.

## Scaling to 100,000 PDFs Per Day

The current CLI implementation is intentionally lightweight for the technical assessment.

For production, the synchronous workflow could be converted into an asynchronous distributed pipeline:

```text
PDF Upload
     |
     v
Object Storage
     |
     v
Message Queue
     |
     v
PDF/Text Extraction Workers
     |
     v
OCR for Scanned Documents
     |
     v
LLM Processing Workers
     |
     v
Pydantic Validation
     |
     v
Business Rule Engine
     |
     +------------------+
     |                  |
     v                  v
Database          Human Review Queue
```

### Scaling Considerations

To support 100,000 documents per day, the system should use:

* A message queue to distribute documents across workers.
* Multiple processing workers for horizontal scaling.
* Object storage for original PDFs.
* PDF text extraction and OCR for scanned documents.
* Retry mechanisms with exponential backoff.
* API rate-limit and concurrency controls.
* Dead-letter queues for repeatedly failed documents.
* Idempotent processing to prevent duplicate work.
* Structured logging and monitoring.
* Database storage for processing status and validation results.
* Autoscaling based on queue depth.
* Document hashing or caching to avoid unnecessary repeated processing.
* Secure handling of sensitive freight information.

100,000 documents per day is approximately:

```text
100,000 / 86,400 ≈ 1.16 documents/second
```

This is only the average throughput. A production system should support significantly higher burst capacity by scaling workers horizontally and buffering incoming documents through a queue.

## Reliability and Error Handling

The application handles several failure cases:

* Empty input documents
* LLM API failures
* Empty LLM responses
* Invalid JSON returned by the LLM
* Pydantic validation failures
* Business-rule violations

The parser and validator are separated so that API failures and data-quality failures can be handled independently.

## Security

* API credentials are stored in `.env`.
* `.env` is excluded from Git using `.gitignore`.
* `.env.example` contains only variable names/placeholders.
* Production deployments should use a secure secret manager.
* Sensitive freight document contents should not be written to application logs.
* Stored documents should use appropriate access controls.
* Production systems should follow least-privilege principles.

## Current Status

The technical assessment workflow is implemented and tested:

* LLM document extraction: implemented
* Typed Pydantic schema: implemented
* JSON validation: implemented
* Rate mismatch validation: implemented
* Overweight validation: implemented
* Incomplete data validation: implemented
* Automated validation tests: implemented
* End-to-end workflow test: implemented
* Sample output: included
* Production scaling architecture: documented
* Environment configuration: documented

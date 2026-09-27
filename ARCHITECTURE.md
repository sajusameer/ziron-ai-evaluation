# Architecture & Scaling Notes

## 1. Current Architecture

The current implementation follows a simple modular pipeline:

```text
Raw Freight Document
        |
        v
+-------------------+
|   LLM Parser      |
|    parser.py      |
+---------+---------+
          |
          v
+-------------------+
| Pydantic Models   |
|    models.py      |
+---------+---------+
          |
          v
+-------------------+
| Business Rules    |
|   validator.py    |
+---------+---------+
          |
          v
+-------------------+
| Decision Layer    |
|     main.py       |
+-------------------+
          |
       +--+--+
       |     |
       v     v
   APPROVED  FLAGGED_FOR_HUMAN_REVIEW
```

## 2. Responsibilities

### LLM Parser

The LLM is responsible only for extracting structured information from the unstructured freight document.

It should not calculate or correct financial values.

This separation prevents the LLM from making business decisions.

### Pydantic Schema

Pydantic provides strict typed validation for the extracted JSON.

If the LLM response does not match the expected structure, the parser rejects it instead of passing invalid data to the business-rule layer.

### Business Rule Engine

Business rules are implemented deterministically in Python.

For example:

```text
total_linehaul_rate + fuel_surcharge == total_pay
```

and:

```text
weight_lbs > 45,000
```

This makes important business decisions predictable and testable.

### Decision Layer

The decision layer combines validation results and returns either:

```text
APPROVED
```

or:

```text
FLAGGED_FOR_HUMAN_REVIEW
```

with the detected validation reasons.

---

# 3. Scaling to 100,000 PDFs Per Day

The current CLI implementation is suitable for the evaluation task. A production system processing 100,000 PDFs per day should use an asynchronous, distributed architecture.

A possible production architecture:

```text
                 +----------------+
                 |  PDF Upload    |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 | Object Storage |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 |  Message Queue |
                 +-------+--------+
                         |
              +----------+----------+
              |          |          |
              v          v          v
          +-------+  +-------+  +-------+
          |Worker |  |Worker |  |Worker |
          |   1   |  |   2   |  |   N   |
          +---+---+  +---+---+  +---+---+
              |          |          |
              +----------+----------+
                         |
                         v
                 +----------------+
                 | PDF/Text/OCR   |
                 | Extraction     |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 | LLM Processing  |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 | Pydantic Schema |
                 | Validation      |
                 +-------+--------+
                         |
                         v
                 +----------------+
                 | Business Rules  |
                 +-------+--------+
                         |
                    +----+----+
                    |         |
                    v         v
                Approved    Human Review
                    |         |
                    +----+----+
                         |
                         v
                 +----------------+
                 |    Database    |
                 +----------------+
```

## 4. Queue-Based Processing

A message queue should be placed between document ingestion and processing workers.

Examples include:

* Amazon SQS
* Kafka
* RabbitMQ

The queue allows workers to process documents independently and makes it easier to scale horizontally.

If processing demand increases, additional workers can be started without changing the extraction or validation logic.

## 5. PDF and OCR Processing

Not every freight document will contain machine-readable text.

The production pipeline should therefore support:

1. Normal PDF text extraction
2. OCR for scanned documents
3. Text normalization
4. LLM structured extraction

This prevents scanned documents from failing before reaching the parser.

## 6. LLM Reliability

LLM API calls should include:

* Retry with exponential backoff
* Timeout handling
* Rate-limit handling
* Concurrency limits
* Structured output/schema enforcement
* Provider failure handling
* Logging of processing status

A dead-letter queue can be used for documents that repeatedly fail.

## 7. Idempotency

Each document should have a unique processing ID or document hash.

Before processing a document, the system can check whether it has already been processed.

This prevents duplicate LLM calls and duplicate records.

## 8. Observability

A production system should monitor:

* Documents received
* Documents successfully processed
* LLM failures
* Validation failures
* Average processing time
* Queue depth
* Worker utilization
* Human-review volume
* API rate-limit errors

Structured logs and metrics should be used instead of printing sensitive document contents.

## 9. Security

Sensitive freight information should be protected throughout the pipeline.

Recommended practices:

* Store API credentials in a secret manager.
* Never commit API keys to Git.
* Do not log sensitive freight document contents.
* Encrypt stored documents.
* Use least-privilege access controls.
* Restrict access to human-review data.

## 10. Throughput Consideration

100,000 documents per day is approximately:

```text
100,000 / 86,400 ≈ 1.16 documents/second
```

This is the average throughput.

The production architecture should support significantly higher burst capacity because documents may arrive unevenly throughout the day.

Horizontal worker scaling and queue-based processing make this possible.

## 11. Separation of Concerns

The most important architectural principle is keeping extraction separate from business validation:

```text
LLM
 ↓
Structured Data
 ↓
Deterministic Validation
 ↓
Business Decision
```

The LLM handles the unstructured language problem, while Python handles deterministic business rules.

This makes the system easier to test, debug, replace, and scale.

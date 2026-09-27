# from pathlib import Path

# from app.parser import parse_freight_document


# def main():
#     file_path = Path("data/sample.txt")
#     raw_text = file_path.read_text(encoding="utf-8")

#     document = parse_freight_document(raw_text)

#     print("Parsed Document:")
#     print(document.model_dump_json(indent=2))


# if __name__ == "__main__":
#     main()

import json
import os
import sys
from dotenv import load_dotenv
from app.parser import parse_freight_document
from app.validator import validate_freight_document

load_dotenv()


def execute_workflow(text: str):
    # 1. Parse using LLM
    print("Parsing document with LLM...")
    parsed_doc = parse_freight_document(text)

    # 2. Validate using rule engine
    print("Running validation rules...")
    errors, warnings = validate_freight_document(parsed_doc)
    all_flags = errors + warnings

    # 3. Decision workflow
    if not all_flags:
        result = {
            "status": "APPROVED",
            "data": parsed_doc.model_dump(),
        }
    else:
        result = {
            "status": "FLAGGED_FOR_HUMAN_REVIEW",
            "flag_reasons": all_flags,
            "data": parsed_doc.model_dump(),
        }

    return result


if __name__ == "__main__":
    # sample.txt থেকে টেস্ট ডেটা পড়া
    input_file = sys.argv[1] if len(sys.argv) > 1 else "sample.txt"

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        raw_text = f.read()

    output = execute_workflow(raw_text)

    print("\n--- WORKFLOW RESULT ---")
    print(json.dumps(output, indent=2))
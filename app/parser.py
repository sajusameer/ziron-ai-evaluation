import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import FreightDocument


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not configured. "
        "Please add it to your .env file."
    )


client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=api_key,
)


def parse_freight_document(raw_text: str) -> FreightDocument:
    if not raw_text.strip():
        raise ValueError("Input freight document is empty.")

    schema = FreightDocument.model_json_schema()

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You extract structured data from freight documents. "
                        "Extract only the required fields. "
                        "Do not calculate or correct financial values. "
                        "Return the values exactly as stated in the document. "
                        "If a required field is missing or ambiguous, "
                        "do not invent a value. "
                        f"Return valid JSON matching this schema exactly: "
                        f"{json.dumps(schema)}"
                    ),
                },
                {
                    "role": "user",
                    "content": raw_text,
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
        )

    except Exception as exc:
        raise RuntimeError(
            f"LLM API request failed: {exc}"
        ) from exc

    content = response.choices[0].message.content

    if not content:
        raise ValueError("LLM returned an empty response.")

    try:
        return FreightDocument.model_validate_json(content)
    except Exception as exc:
        raise ValueError(
            f"LLM returned invalid freight document JSON: {exc}"
        ) from exc
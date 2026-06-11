import json
import re
from ollama import chat

def llm_extract_headers(headers):
    formatted_headers = "\n".join(
        [
            f"{i}. {header}"
            for i, header in enumerate(headers)
        ]
    )

    prompt = f"""
You are extracting structured information from CSM note headers.

For EACH header return:

{{
    "date": "YYYY/MM/DD or null",
    "account_id": integer or null,
    "company_name": string or null
}}

Assume year is 2026 unless explicitly specified.

Return ONLY a JSON array.

Example:

[
    {{
        "date": "2026/03/15",
        "account_id": 1001,
        "company_name": "BrightPath Solutions"
    }}
]

Headers:

{formatted_headers}
"""

    response = chat(
        model="qwen3:8b",
        think=False,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response["message"]["content"]
    text = content.strip()

    # Remove thinking blocks
    text = re.sub( r"<think>.*?</think>", "", text, flags=re.DOTALL )
    # Remove markdown fences
    text = re.sub( r"^```json\s*", "", text )
    text = re.sub( r"^```\s*", "", text )
    text = re.sub( r"\s*```$", "", text )

    return json.loads( text.strip() )


from ollama import chat
from llm_utils import clean_llm_response, extract_json_array


def llm_extract_headers(headers):
    formatted_headers = "\n".join(
        f"{i}. {header}" for i, header in enumerate(headers)
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
        messages=[{"role": "user", "content": prompt}]
    )

    text = clean_llm_response(response["message"]["content"])
    return extract_json_array(text)
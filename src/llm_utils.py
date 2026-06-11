import re
import json


def clean_llm_response(text: str) -> str:
    """Strip think blocks and code fences from LLM output."""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    text = re.sub(r"```(?:json)?\s*", "", text)
    return text.strip()


def extract_json_array(text: str) -> list:
    """Extract and parse the outermost JSON array using bracket matching."""
    start = text.find("[")
    if start == -1:
        raise ValueError("No JSON array found in response")

    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON array: {e}\nRaw: {text[start:i + 1][:300]}")

    raise ValueError("Unmatched '[' — JSON array not closed")
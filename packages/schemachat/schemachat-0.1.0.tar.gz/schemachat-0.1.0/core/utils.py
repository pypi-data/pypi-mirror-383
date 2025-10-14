import json
from typing import Type, TypeVar

from pydantic import BaseModel

M = TypeVar("M", bound=BaseModel)


def ensure_json_format(text: str, response_model: Type[M]) -> M:
    try:
        return response_model.model_validate_json(text)
    except Exception:
        # Fallback: try to extract JSON from response
        # Find all potential JSON objects by looking for balanced braces
        start_pos = 0
        while True:
            start = text.find("{", start_pos)
            if start == -1:
                break
            
            brace_count = 0
            end = -1
            
            for i in range(start, len(text)):
                if text[i] == "{":
                    brace_count += 1
                elif text[i] == "}":
                    brace_count -= 1
                    if brace_count == 0:
                        end = i
                        break
            
            if end != -1:
                json_content = text[start : end + 1]
                try:
                    data = json.loads(json_content)
                    return response_model.model_validate(data)
                except (json.JSONDecodeError, ValueError):
                    # Try the next potential JSON object
                    start_pos = start + 1
                    continue
            else:
                break
        
        raise

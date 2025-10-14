import json
import requests
from .codegen import CODE_GEN_SCHEMA

SYSTEM_PROMPT = (
    "You are a hardware register analyzer. From the given text, extract registers and bitfields.\n"
    "- For each bitfield, RETURN ITS LSB (0-based) and bit width.\n"
    "- Order fields by LSB ascending (LSB -> MSB).\n"
    "- Do NOT include reserved fields; ONLY return real fields. (Gaps will be filled automatically.)\n"
    "- The sum of (widths + reserved gaps) is 32 bits per register.\n"
    "Return strictly in the provided JSON schema."
)

def call_gemini(doc_text: str, api_url: str, api_key: str):
    payload = {
        "contents": [{"parts": [{"text": doc_text}]}],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": CODE_GEN_SCHEMA
        }
    }

    headers = {'Content-Type': 'application/json'}
    resp = requests.post(f"{api_url}?key={api_key}", headers=headers, data=json.dumps(payload))
    resp.raise_for_status()
    data = resp.json()

    # 후보 텍스트 추출
    try:
        response_text = data['candidates'][0]['content']['parts'][0]['text']
    except (KeyError, IndexError, TypeError):
        if isinstance(data, dict) and "text" in data:
            response_text = data["text"]
        else:
            raise RuntimeError(f"Unexpected Gemini response structure: {json.dumps(data)[:1000]}")

    # JSON 파싱 (코드펜스 방어)
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        cleaned = response_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = "\n".join(
                line for line in cleaned.splitlines()
                if not line.strip().startswith(("json", "JSON"))
            )
        return json.loads(cleaned)

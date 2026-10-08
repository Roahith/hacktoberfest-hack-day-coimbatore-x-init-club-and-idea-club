import json
import os

from dotenv import load_dotenv
from google import genai

load_dotenv(".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemma-4-26b-a4b-it"


def analyze_screening(
    risk_level: str,
    risk_score: int,
    reasons: list[str],
) -> dict:
    """Use Gemma 4 to explain the deterministic screening result."""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = f"""You are VeriLens AI.
Explain this screening result in 1 short sentence.

Risk: {risk_level}
Score: {risk_score}
Reasons: {json.dumps(reasons)}

Return ONLY JSON:
{{"summary":"short explanation","recommendation":"CLEAR or SECONDARY_REVIEW"}}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0.1,
            "max_output_tokens": 80,
        },
    )

    text = (response.text or "").strip()

    if not text:
        return {
            "summary": (
                "Automated verification signals were evaluated "
                "and the deterministic screening result was used."
            ),
            "recommendation": (
                "CLEAR" if risk_level == "CLEAR"
                else "SECONDARY_REVIEW"
            ),
            "model": MODEL,
            "ai_status": "NO_TEXT_RESPONSE",
        }

    if text.startswith("```"):
        text = text.replace("```json", "", 1)
        text = text.replace("```", "")
        text = text.strip()

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        result = {
            "summary": text,
            "recommendation": (
                "CLEAR" if risk_level == "CLEAR"
                else "SECONDARY_REVIEW"
            ),
        }

    result["model"] = MODEL
    result["ai_status"] = "OK"

    return result

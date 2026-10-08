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

    reasons_text = (
        "; ".join(reasons)
        if reasons
        else "No verification issues were detected."
    )

    prompt = f"""You are the explanation assistant for VeriLens AI.

Explain this screening result in ONE short sentence.

Risk level: {risk_level}
Risk score: {risk_score}
Verification findings: {reasons_text}

Do not make a criminality determination.
Do not make an immigration decision.
Do not invent facts.
Only explain the verification findings.
Return only the final explanation sentence."""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config={
            "temperature": 0.1,
            "max_output_tokens": 1024,
        },
    )

    # Gemma 4 may return separate thinking and final-answer parts.
    # We explicitly select the non-thinking part.
    final_text = None

    if response.candidates:
        for candidate in response.candidates:
            if not candidate.content:
                continue

            for part in candidate.content.parts:
                if getattr(part, "thought", False):
                    continue

                if part.text and part.text.strip():
                    final_text = part.text.strip()
                    break

            if final_text:
                break

    # Fallback to SDK-provided text if available.
    if not final_text:
        final_text = (response.text or "").strip()

    if not final_text:
        return {
            "summary": (
                "Automated verification signals were evaluated "
                "and the deterministic screening result was used."
            ),
            "recommendation": (
                "CLEAR"
                if risk_level == "CLEAR"
                else "SECONDARY_REVIEW"
            ),
            "model": MODEL,
            "ai_status": "NO_TEXT_RESPONSE",
        }

    # Remove accidental markdown code fences.
    final_text = final_text.replace("```", "").strip()

    return {
        "summary": final_text,
        "recommendation": (
            "CLEAR"
            if risk_level == "CLEAR"
            else "SECONDARY_REVIEW"
        ),
        "model": MODEL,
        "ai_status": "OK",
    }

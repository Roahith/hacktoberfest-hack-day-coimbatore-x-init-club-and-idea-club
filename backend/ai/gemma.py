import json
import os
from typing import Any

import requests


HF_API_URL = os.getenv("HF_API_URL")
HF_TOKEN = os.getenv("HF_TOKEN")


SYSTEM_PROMPT = """
You are VeriLens AI, an explainable immigration pre-screening assistant.

You MUST reason only from the structured evidence supplied to you.

Rules:
- Do not invent criminal, security, immigration, or identity facts.
- Do not claim access to INTERPOL or any real government database.
- Security records are synthetic demonstration data.
- The deterministic risk engine has already calculated the risk score.
- Explain why the evidence supports the result.
- The human immigration officer makes the final decision.
- Never make a legal admission decision yourself.

Return concise JSON with:
{
  "summary": "...",
  "key_findings": ["..."],
  "recommendation": "CLEAR or SECONDARY_REVIEW",
  "confidence": "HIGH, MEDIUM, or LOW"
}
"""


def analyze_screening(evidence: dict[str, Any]) -> dict[str, Any]:
    """Send structured screening evidence to the hosted Gemma model."""

    if not HF_API_URL or not HF_TOKEN:
        return {
            "summary": "Gemma cloud inference is not configured.",
            "key_findings": [],
            "recommendation": "SECONDARY_REVIEW",
            "confidence": "LOW",
        }

    prompt = (
        SYSTEM_PROMPT
        + "\n\nSCREENING EVIDENCE:\n"
        + json.dumps(evidence, indent=2)
        + "\n\nAnalyze this evidence."
    )

    response = requests.post(
        HF_API_URL,
        headers={
            "Authorization": f"Bearer {HF_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 400,
                "temperature": 0.1,
                "return_full_text": False,
            },
        },
        timeout=60,
    )

    response.raise_for_status()

    result = response.json()

    if isinstance(result, list) and result:
        generated = result[0].get("generated_text", "")
    elif isinstance(result, dict):
        generated = result.get("generated_text", "")
    else:
        generated = str(result)

    return {
        "raw_response": generated,
        "model": "Gemma 4",
    }

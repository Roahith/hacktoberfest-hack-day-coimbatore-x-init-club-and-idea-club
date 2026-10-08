from backend.schemas.screening import ScreeningEvidence, ScreeningResult


def calculate_risk(evidence: ScreeningEvidence) -> ScreeningResult:
    score = 0
    reasons: list[str] = []

    # Document checks
    if not evidence.document.passport_found:
        score += 40
        reasons.append("Passport record was not found.")

    if not evidence.document.mrz_valid:
        score += 25
        reasons.append("MRZ validation failed.")

    if not evidence.document.fields_match:
        score += 30
        reasons.append("Passport details do not match the verified record.")

    if evidence.document.passport_status == "EXPIRED":
        score += 20
        reasons.append("Passport is expired.")

    for mismatch in evidence.document.mismatches:
        reasons.append(f"Document mismatch: {mismatch}")

    # Immigration checks
    if evidence.immigration.visa_required:
        if not evidence.immigration.visa_found:
            score += 30
            reasons.append("Required visa was not found.")

        elif not evidence.immigration.visa_valid:
            score += 25
            reasons.append("Visa is not valid.")

        if not evidence.immigration.visa_passport_match:
            score += 30
            reasons.append("Visa does not match the passport.")

    for issue in evidence.immigration.issues:
        reasons.append(f"Immigration issue: {issue}")

    # Security checks
    if evidence.security.match:
        score += 60
        reasons.append(
            evidence.security.reason
            or "Security screening produced a match."
        )

    # Biometric checks
    if evidence.biometric.checked and not evidence.biometric.match:
        score += 60
        reasons.append("Live face does not match the passport photograph.")

    # Keep score within 0–100
    score = min(score, 100)

    # Determine risk level
    if score >= 60:
        risk_level = "ALERT"
        recommendation = "SECONDARY_REVIEW"
    elif score >= 25:
        risk_level = "REVIEW"
        recommendation = "SECONDARY_REVIEW"
    else:
        risk_level = "CLEAR"
        recommendation = "CLEAR"

    if reasons:
        explanation = (
            "One or more verification signals require attention: "
            + " ".join(reasons)
        )
    else:
        explanation = (
            "All available verification signals are consistent."
        )

    return ScreeningResult(
        risk_level=risk_level,
        risk_score=score,
        reasons=reasons,
        recommendation=recommendation,
        explanation=explanation,
        evidence=evidence,
    )

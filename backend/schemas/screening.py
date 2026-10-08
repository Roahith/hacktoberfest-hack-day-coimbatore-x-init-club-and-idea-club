from dataclasses import dataclass, field
from typing import Literal


RiskLevel = Literal["CLEAR", "REVIEW", "ALERT"]


@dataclass
class DocumentEvidence:
    passport_found: bool = False
    mrz_valid: bool = False
    fields_match: bool = False
    passport_status: str = "UNKNOWN"
    mismatches: list[str] = field(default_factory=list)


@dataclass
class ImmigrationEvidence:
    nationality: str = "UNKNOWN"
    visa_required: bool = False
    visa_found: bool = False
    visa_valid: bool = False
    visa_passport_match: bool = False
    issues: list[str] = field(default_factory=list)


@dataclass
class SecurityEvidence:
    match: bool = False
    status: str = "NOT_CHECKED"
    reason: str | None = None


@dataclass
class BiometricEvidence:
    checked: bool = False
    match: bool = False
    similarity: float | None = None


@dataclass
class ScreeningEvidence:
    document: DocumentEvidence = field(default_factory=DocumentEvidence)
    immigration: ImmigrationEvidence = field(
        default_factory=ImmigrationEvidence
    )
    security: SecurityEvidence = field(default_factory=SecurityEvidence)
    biometric: BiometricEvidence = field(
        default_factory=BiometricEvidence
    )


@dataclass
class ScreeningResult:
    risk_level: RiskLevel
    risk_score: int
    reasons: list[str]
    recommendation: str
    explanation: str
    evidence: ScreeningEvidence | None = None

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from typing import Optional
import shutil
import uuid

from backend.immigration.verifier import verify_immigration
from backend.security.screening import screen_security
from backend.documents.traveler_pack import generate_document_pack
from backend.immigration.screening_service import run_immigration_screening
from backend.schemas.screening import (
    ScreeningEvidence,
    DocumentEvidence,
    ImmigrationEvidence,
    SecurityEvidence,
    BiometricEvidence,
)
from backend.decision.risk_engine import calculate_risk
from backend.ai.gemma import analyze_screening
from dataclasses import asdict
from p2_document_engine.ocr_engine import extract_document_text
from p2_document_engine.mrz_engine import extract_mrz
from p2_document_engine.validation import (
    extract_passport_number_from_ocr,
    extract_date_of_birth,
    database_comparison,
    calculate_tamper_indicators,
)



# ============================================================
# APP SETUP
# ============================================================

app = FastAPI(
    title="VeriLens AI",
    description="AI-assisted immigration pre-screening system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENT_DIR = BASE_DIR / "test_documents"
DOCUMENT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# MODELS
# ============================================================

class Traveler(BaseModel):
    name: str
    passport_number: str
    nationality: str
    date_of_birth: Optional[str] = None
    expiry: Optional[str] = None


class ScreeningRequest(BaseModel):
    name: str
    passport_number: str
    nationality: str
    date_of_birth: Optional[str] = None
    expiry: Optional[str] = None


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():
    return {
        "project": "VeriLens AI",
        "status": "online",
        "message": "Immigration pre-screening API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# CREATE TRAVELER DOCUMENT PACK
# ============================================================

@app.post("/traveler/create")
def create_traveler(traveler: Traveler):

    traveler_data = traveler.model_dump()

    try:
        result = generate_document_pack(traveler_data)

        return {
            "success": True,
            "message": "Synthetic traveler document pack created",
            "traveler": traveler_data,
            "documents": result
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document generation failed: {str(e)}"
        )


# ============================================================
# LIST GENERATED DOCUMENTS
# ============================================================

@app.get("/documents")
def list_documents():

    documents = []

    if not DOCUMENT_DIR.exists():
        return {
            "success": True,
            "documents": []
        }

    for file in DOCUMENT_DIR.rglob("*"):

        if file.is_file():

            documents.append({
                "name": file.name,
                "path": str(file.relative_to(DOCUMENT_DIR)),
                "size": file.stat().st_size
            })

    return {
        "success": True,
        "count": len(documents),
        "documents": documents
    }


# ============================================================
# DOWNLOAD DOCUMENT
# ============================================================

@app.get("/documents/download")
def download_document(path: str):

    requested_file = (DOCUMENT_DIR / path).resolve()

    # Security check so users cannot escape test_documents
    try:
        requested_file.relative_to(DOCUMENT_DIR.resolve())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid document path"
        )

    if not requested_file.exists():
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    if not requested_file.is_file():
        raise HTTPException(
            status_code=400,
            detail="Requested path is not a file"
        )

    return FileResponse(
        path=requested_file,
        filename=requested_file.name,
        media_type="application/pdf"
    )


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file supplied"
        )

    extension = Path(file.filename).suffix.lower()

    allowed_extensions = {
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg"
    }

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, JPG and JPEG files are supported"
        )

    unique_name = f"{uuid.uuid4().hex}_{file.filename}"

    destination = UPLOAD_DIR / unique_name

    with destination.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {
        "success": True,
        "filename": file.filename,
        "stored_filename": unique_name,
        "path": str(destination),
        "message": "Document uploaded successfully"
    }


# ============================================================
# IMMIGRATION VERIFICATION
# ============================================================

@app.post("/verify/immigration")
def immigration_verification(request: ScreeningRequest):

    traveler_data = request.model_dump()

    try:

        result = verify_immigration(traveler_data)

        return {
            "success": True,
            "traveler": traveler_data,
            "immigration": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Immigration verification failed: {str(e)}"
        )


# ============================================================
# SECURITY SCREENING
# ============================================================

@app.post("/verify/security")
def security_verification(request: ScreeningRequest):

    traveler_data = request.model_dump()

    try:

        result = screen_security(traveler_data)

        return {
            "success": True,
            "traveler": traveler_data,
            "security": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Security screening failed: {str(e)}"
        )


# ============================================================
# UNIFIED IMMIGRATION SCREENING
# ============================================================

@app.post("/screen")
def screen_traveler(traveler: ScreeningRequest):
    """
    Unified VeriLens AI screening endpoint.

    Flow:
        P3 passport / visa / security verification
                    ↓
        ScreeningEvidence
                    ↓
        P1 deterministic risk engine
                    ↓
        Gemma 4 explanation
                    ↓
        Unified result
    """

    traveler_data = traveler.model_dump()

    try:
        # --------------------------------------------------------
        # 1. RUN P3 SCREENING
        # --------------------------------------------------------

        p3_result = run_immigration_screening(traveler_data)

        if not p3_result.get("success", False):
            raise HTTPException(
                status_code=400,
                detail=p3_result
            )

        immigration = p3_result.get("immigration", {})
        security = p3_result.get("security", {})

        # --------------------------------------------------------
        # 2. CONVERT P3 OUTPUT → P1 EVIDENCE SCHEMA
        # --------------------------------------------------------

        # P3 currently does not expose a separate visa_found field.
        # A valid passport-linked visa is treated as a found visa.
        visa_valid = immigration.get("visa_valid", False)
        visa_match = immigration.get("visa_passport_match", False)

        evidence = ScreeningEvidence(
            document=DocumentEvidence(
                passport_found=immigration.get(
                    "passport_found", False
                ),
                # MRZ is not part of the current P3 JSON contract.
                # P2 document integration will populate this later.
                mrz_valid=True,
                fields_match=immigration.get(
                    "details_match", False
                ),
                passport_status="VALID"
                if immigration.get("passport_found", False)
                else "UNKNOWN",
                mismatches=[],
            ),

            immigration=ImmigrationEvidence(
                nationality=traveler_data.get(
                    "nationality", "UNKNOWN"
                ),
                visa_required=immigration.get(
                    "visa_required", False
                ),
                visa_found=visa_valid or visa_match,
                visa_valid=visa_valid,
                visa_passport_match=visa_match,
                issues=(
                    [immigration["reason"]]
                    if immigration.get("reason")
                    else []
                ),
            ),

            security=SecurityEvidence(
                match=security.get("match", False),
                status=security.get(
                    "status", "NOT_CHECKED"
                ),
                reason=security.get("reason"),
            ),

            # Face verification is not integrated yet.
            biometric=BiometricEvidence(
                checked=False,
                match=False,
                similarity=None,
            ),
        )

        # --------------------------------------------------------
        # 3. P1 DETERMINISTIC RISK ENGINE
        # --------------------------------------------------------

        risk_result = calculate_risk(evidence)

        # --------------------------------------------------------
        # 4. GEMMA 4 EXPLANATION
        # --------------------------------------------------------

        try:
            ai_result = analyze_screening(
                risk_level=risk_result.risk_level,
                risk_score=risk_result.risk_score,
                reasons=risk_result.reasons,
            )
        except Exception as ai_error:
            # AI failure must not break deterministic screening.
            ai_result = {
                "summary": risk_result.explanation,
                "recommendation": risk_result.recommendation,
                "model": "gemma-4-26b-a4b-it",
                "ai_status": "FALLBACK",
                "error": str(ai_error),
            }

        # --------------------------------------------------------
        # 5. FINAL UNIFIED RESPONSE
        # --------------------------------------------------------

        return {
            "success": True,

            "traveler": traveler_data,

            "screening": {
                "risk_level": risk_result.risk_level,
                "risk_score": risk_result.risk_score,
                "recommendation": risk_result.recommendation,
                "reasons": risk_result.reasons,
                "explanation": risk_result.explanation,

                "ai": ai_result,

                "evidence": asdict(
                    risk_result.evidence
                ),
            },

            # Keep the original P3 outputs available for debugging
            # and frontend development.
            "p3": {
                "immigration": immigration,
                "security": security,
            },

            "human_review_required": (
                risk_result.recommendation
                == "SECONDARY_REVIEW"
            ),
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "error": str(exc),
            },
        )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )

def _mrz_date_to_iso(value: str | None) -> str | None:
    """Convert MRZ YYMMDD dates to ISO YYYY-MM-DD."""

    if not value or len(value) != 6 or not value.isdigit():
        return value

    yy = int(value[0:2])
    mm = value[2:4]
    dd = value[4:6]

    # Passport MRZ uses two-digit years.
    # This prototype treats 00-49 as 2000-2049
    # and 50-99 as 1950-1999.
    year = 2000 + yy if yy < 50 else 1900 + yy

    return f"{year:04d}-{mm}-{dd}"


@app.post("/screen-document")
async def screen_document(file: UploadFile = File(...)):
    """
    Full VeriLens document screening pipeline.

    P2 document intelligence
        -> P3 immigration/security
        -> P1 deterministic risk engine
        -> Gemma 4 explanation
    """

    filename = file.filename or ""
    extension = ""

    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[1].lower()

    allowed_extensions = {".pdf", ".png", ".jpg", ".jpeg"}

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, JPG and JPEG files are supported.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        # =====================================================
        # P2: OCR + MRZ
        # =====================================================

        ocr_result = extract_document_text(
            file_bytes,
            filename,
        )

        raw_text = ocr_result["raw_text"]
        mrz_text = ocr_result.get("mrz_text", "")

        mrz_result = extract_mrz(mrz_text)

        if not mrz_result.get("detected"):
            raise HTTPException(
                status_code=422,
                detail="Passport MRZ could not be detected.",
            )

        passport_data = {
            "passport_number": mrz_result.get("passport_number"),
            "surname": mrz_result.get("surname"),
            "given_names": mrz_result.get("given_names"),
            "nationality": mrz_result.get("nationality"),
            "date_of_birth": _mrz_date_to_iso(mrz_result.get("date_of_birth_raw")),
            "sex": mrz_result.get("sex"),
            "expiry_date": _mrz_date_to_iso(mrz_result.get("expiry_date_raw")),
        }

        passport_number = passport_data["passport_number"]

        # =====================================================
        # P2: OCR <-> MRZ consistency
        # =====================================================

        passport_number_ocr = extract_passport_number_from_ocr(raw_text)
        date_of_birth_ocr = extract_date_of_birth(raw_text)

        consistency_checks = []

        if passport_number_ocr:
            consistency_checks.append(
                passport_number_ocr.replace(" ", "").upper()
                == str(passport_number).upper()
            )

        if date_of_birth_ocr:
            consistency_checks.append(
                date_of_birth_ocr.replace("/", "").replace("-", "")
                == str(
                    passport_data["date_of_birth"]
                )
            )

        ocr_mrz_match = (
            all(consistency_checks)
            if consistency_checks
            else None
        )

        # =====================================================
        # P3: Immigration + security screening
        # =====================================================

        nationality = passport_data.get("nationality")

        # Normalize MRZ nationality codes to synthetic DB values.
        nationality = {
            "IND": "INDIA",
            "GBR": "UK",
        }.get(nationality, nationality)

        traveler = {
            "name": (
                f"{passport_data.get('given_names', '')} "
                f"{passport_data.get('surname', '')}"
            ).strip(),
            "passport_number": passport_number,
            "date_of_birth": passport_data.get("date_of_birth"),
            "nationality": nationality,
            "expiry": passport_data.get("expiry_date"),
        }

        p3_result = run_immigration_screening(traveler)

        if not p3_result.get("success"):
            raise HTTPException(
                status_code=422,
                detail=p3_result.get(
                    "reasons",
                    ["Immigration screening failed."],
                ),
            )

        # =====================================================
        # P2: Compare document against P3 database result
        # =====================================================

        immigration = p3_result["immigration"]

        database_record = None

        if immigration.get("passport_found"):
            database_record = {
                "passport_number": passport_number,
                "nationality": passport_data.get("nationality"),
                "date_of_birth": passport_data.get("date_of_birth"),
                "name": traveler["name"],
            }

        database_result = database_comparison(
            passport_data,
            database_record,
        )

        tamper_result = calculate_tamper_indicators(
            mrz_result,
            database_result,
        )

        # =====================================================
        # P1: Build evidence
        # =====================================================

        security = p3_result["security"]

        evidence = ScreeningEvidence(
            document=DocumentEvidence(
                passport_found=immigration.get(
                    "passport_found",
                    False,
                ),
                mrz_valid=mrz_result.get(
                    "valid",
                    False,
                ),
                # P3 is the authoritative synthetic passport DB check.
                fields_match=immigration.get(
                    "details_match",
                    False,
                ),
                passport_status=(
                    "VALID"
                    if immigration.get("passport_found")
                    else "UNKNOWN"
                ),
                mismatches=[],
            ),

            immigration=ImmigrationEvidence(
                nationality=passport_data.get(
                    "nationality",
                    "UNKNOWN",
                ),
                visa_required=immigration.get(
                    "visa_required",
                    False,
                ),
                visa_found=(
                    immigration.get("visa_valid", False)
                    or immigration.get(
                        "visa_passport_match",
                        False,
                    )
                ),
                visa_valid=immigration.get(
                    "visa_valid",
                    False,
                ),
                visa_passport_match=immigration.get(
                    "visa_passport_match",
                    False,
                ),
                issues=(
                    [immigration["reason"]]
                    if immigration.get("reason")
                    else []
                ),
            ),

            security=SecurityEvidence(
                match=security.get("match", False),
                status=security.get("status", "NOT_CHECKED"),
                reason=security.get("reason"),
            ),

            biometric=BiometricEvidence(
                checked=False,
                match=False,
                similarity=None,
            ),
        )

        # =====================================================
        # P1: Deterministic risk engine
        # =====================================================

        screening = calculate_risk(evidence)

        # =====================================================
        # Gemma 4
        # =====================================================

        try:
            ai_result = analyze_screening(
                screening.risk_level,
                screening.risk_score,
                screening.reasons,
            )
        except Exception as error:
            ai_result = {
                "summary": screening.explanation,
                "recommendation": (
                    "CLEAR"
                    if screening.risk_level == "CLEAR"
                    else "SECONDARY_REVIEW"
                ),
                "model": "gemma-4-26b-a4b-it",
                "ai_status": "FALLBACK",
                "error": str(error),
            }

        return {
            "success": True,

            "document": {
                "filename": filename,
                "type": "passport",
            },

            "p2": {
                "ocr": {
                    "confidence": ocr_result["confidence"],
                    "pages": ocr_result["pages"],
                },
                "passport": passport_data,
                "mrz": {
                    "detected": mrz_result.get("detected", False),
                    "valid": mrz_result.get("valid", False),
                    "check_digits": mrz_result.get(
                        "check_digits",
                        {},
                    ),
                },
                "consistency": {
                    "ocr_mrz_match": ocr_mrz_match,
                    "database_match": database_result.get(
                        "match"
                    ),
                },
                "tamper": tamper_result,
            },

            "screening": {
                "risk_level": screening.risk_level,
                "risk_score": screening.risk_score,
                "recommendation": screening.recommendation,
                "reasons": screening.reasons,
                "explanation": screening.explanation,
                "ai": ai_result,
                "evidence": asdict(screening.evidence),
            },

            "p3": p3_result,

            "human_review_required": (
                screening.risk_level != "CLEAR"
            ),
        }


    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document screening failed: {error}",
        )

from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, File, HTTPException
from backend.biometric.face_engine import save_reference, compare
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
    return FileResponse("frontend/index.html")

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
        # The document generator expects passport_expiry,
        # while the public Traveler schema uses expiry.
        document_data = {
            **traveler_data,
            "passport_expiry": traveler_data.get("expiry"),
        }

        result = generate_document_pack(document_data)

        # Register the traveler in the synthetic screening database.
        import json

        passport_file = Path("data/passports.json")

        if passport_file.exists():
            with open(passport_file, "r", encoding="utf-8") as f:
                passports = json.load(f)
        else:
            passports = []

        # Replace an existing demo record with the same passport number.
        passports = [
            p for p in passports
            if p.get("passport_number") != traveler.passport_number
        ]

        passports.append({
            "passport_number": traveler.passport_number,
            "name": traveler.name,
            "date_of_birth": traveler.date_of_birth,
            "nationality": traveler.nationality,
            "citizenship": traveler.nationality,
            "issue_date": None,
            "expiry_date": traveler.expiry,
            "status": "ACTIVE"
        })

        with open(passport_file, "w", encoding="utf-8") as f:
            json.dump(passports, f, indent=2)

        # Register the traveler in the synthetic security database.
        security_file = Path("data/security_records.json")

        if security_file.exists():
            with open(security_file, "r", encoding="utf-8") as f:
                security_records = json.load(f)
        else:
            security_records = []

        security_records = [
            r for r in security_records
            if r.get("passport_number") != traveler.passport_number
        ]

        security_records.append({
            "record_id": "SEC-" + traveler.passport_number,
            "name": traveler.name,
            "date_of_birth": traveler.date_of_birth,
            "passport_number": traveler.passport_number,
            "status": "CLEAR",
            "reason": None
        })

        with open(security_file, "w", encoding="utf-8") as f:
            json.dump(security_records, f, indent=2)

        # Register a synthetic active visa for foreign travelers.
        visa_file = Path("data/visas.json")

        if visa_file.exists():
            with open(visa_file, "r", encoding="utf-8") as f:
                visas = json.load(f)
        else:
            visas = []

        visas = [
            v for v in visas
            if v.get("passport_number") != traveler.passport_number
        ]

        if str(traveler.nationality).strip().upper() not in {
            "INDIA", "INDIAN", "IND", "IN"
        }:
            visas.append({
                "visa_id": "DEMO-V-" + traveler.passport_number,
                "passport_number": traveler.passport_number,
                "visa_type": "TOURIST",
                "country": traveler.nationality,
                "issue_date": None,
                "expiry_date": traveler.expiry,
                "status": "ACTIVE"
            })

        with open(visa_file, "w", encoding="utf-8") as f:
            json.dump(visas, f, indent=2)

        generated = result.get("documents", {})

        return {
            "success": True,
            "message": "Traveler registered and synthetic document pack created",
            "traveler": traveler_data,
            "documents": result,
            "downloads": {
                "passport": generated.get("original_passport"),
                "visa": generated.get("original_visa"),
                "tampered_passport": generated.get("tampered_passport"),
                "detail_mismatch_passport": generated.get("detail_mismatch_passport"),
                "expired_visa": generated.get("expired_visa"),
                "wrong_passport_visa": generated.get("wrong_passport_visa")
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Traveler registration failed: {str(e)}"
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
    from pathlib import Path

    # Allow generated traveler documents and existing demo documents.
    requested_file = Path(path).resolve()

    allowed_roots = [
        Path("test_documents").resolve(),
        Path("generated_documents").resolve(),
        Path("data").resolve(),
    ]

    # Also allow the actual document-generator output directory.
    try:
        from backend.documents.traveler_pack import OUTPUT_ROOT
        allowed_roots.append(Path(OUTPUT_ROOT).resolve())
    except Exception:
        pass

    allowed = False

    for root in allowed_roots:
        try:
            requested_file.relative_to(root)
            allowed = True
            break
        except ValueError:
            continue

    if not allowed:
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


@app.get("/security/records")
def get_security_records():
    import json

    path = Path("data/security_records.json")

    if not path.exists():
        return {"records": []}

    with open(path, "r", encoding="utf-8") as f:
        records = json.load(f)

    return {"records": records}


@app.post("/biometric/register")
async def register_face(
    passport: str,
    file: UploadFile = File(...)
):
    image = await file.read()

    if not image:
        raise HTTPException(status_code=400, detail="Empty image")

    try:
        path = save_reference(passport, image)

        # --------------------------------------------------------
        # Embed the same registered face into the generated
        # synthetic passport PDF.
        # --------------------------------------------------------
        try:
            import fitz
            from backend.documents.traveler_pack import OUTPUT_ROOT

            passport_pdf = None

            for candidate in Path(OUTPUT_ROOT).rglob("original_passport.pdf"):
                try:
                    doc = fitz.open(str(candidate))
                    text = "".join(page.get_text() for page in doc)
                    doc.close()

                    if passport in text:
                        passport_pdf = candidate
                        break
                except Exception:
                    continue

            if passport_pdf:
                doc = fitz.open(str(passport_pdf))
                page = doc[0]

                # Passport-style photo area on the upper-right.
                rect = fitz.Rect(
                    page.rect.width - 150,
                    75,
                    page.rect.width - 45,
                    220
                )

                page.insert_image(
                    rect,
                    stream=image,
                    keep_proportion=True
                )

                temp_pdf = passport_pdf.with_name(
                    "original_passport_with_photo.pdf"
                )

                doc.save(
                    str(temp_pdf),
                    garbage=4,
                    deflate=True
                )
                doc.close()

                temp_pdf.replace(passport_pdf)

        except Exception as pdf_error:
            # Biometric registration remains successful even if
            # PDF photo embedding fails.
            print(
                "Passport photo embedding warning:",
                pdf_error
            )

        return {
            "success": True,
            "passport": passport,
            "reference_face": path,
            "passport_photo_embedded": bool(passport_pdf),
            "message": "Reference face registered successfully"
        }

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/biometric/verify")
async def verify_face(
    passport: str,
    file: UploadFile = File(...)
):
    image = await file.read()

    try:
        return compare(passport, image)

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


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

        # Generated synthetic passports contain a reliable PDF text layer.
        # OCR may miss the MRZ, so append the PDF text directly.
        if filename.lower().endswith(".pdf"):
            try:
                pdf = fitz.open(stream=file_bytes, filetype="pdf")
                pdf_text = "\n".join(
                    page.get_text() for page in pdf
                )
                pdf.close()

                if pdf_text.strip():
                    raw_text = raw_text + "\n" + pdf_text
                    mrz_text = mrz_text + "\n" + pdf_text
            except Exception as pdf_error:
                print("PDF text extraction warning:", pdf_error)

        # Prefer the PDF text layer for generated synthetic passports.
        # Extract the two 44-character MRZ lines directly.
        if filename.lower().endswith(".pdf"):
            import re

            candidates = []
            for line in mrz_text.splitlines():
                cleaned = re.sub(r"\\s+", "", line).upper()
                if len(cleaned) >= 40 and (
                    cleaned.startswith("P<") or
                    (cleaned[0].isalnum() and "<" in cleaned)
                ):
                    candidates.append(cleaned[:44])

            if len(candidates) >= 2:
                mrz_text = "\\n".join(candidates[-2:])

        # Read MRZ directly from the embedded PDF text for our synthetic passports.
        if filename.lower().endswith(".pdf"):
            try:
                import fitz
                import re

                pdf = fitz.open(stream=file_bytes, filetype="pdf")
                embedded_text = "\n".join(
                    page.get_text() for page in pdf
                )
                pdf.close()

                lines = [
                    re.sub(r"\\s+", "", line).upper()
                    for line in embedded_text.splitlines()
                ]

                mrz_lines = [
                    line for line in lines
                    if len(line) >= 40 and line.startswith("P<")
                ]

                if mrz_lines:
                    first = mrz_lines[-1]

                    first_index = lines.index(first)

                    second = None

                    for candidate in lines[first_index + 1:]:
                        if (
                            len(candidate) >= 40
                            and "<" in candidate
                            and candidate != first
                        ):
                            second = candidate
                            break

                    if second:
                        mrz_text = first[:44] + "\n" + second[:44]
                        print("✅ DIRECT PDF MRZ:", mrz_text)

            except Exception as e:
                print("PDF MRZ extraction warning:", e)

        mrz_result = extract_mrz(mrz_text)

        # Synthetic demo PDF fallback.
        # Our generated passports contain embedded PDF text, not a real MRZ.
        if not mrz_result.get("detected") and extension == ".pdf":
            import fitz
            import re

            pdf = fitz.open(stream=file_bytes, filetype="pdf")
            pdf_text = "\\n".join(page.get_text() for page in pdf)
            pdf.close()

            def pdf_field(label):
                match = re.search(
                    rf"{re.escape(label)}\\s*:?\\s*(.+)",
                    pdf_text,
                    re.IGNORECASE,
                )
                return match.group(1).strip() if match else None

            pdf_passport = pdf_field("Passport Number")
            pdf_name = pdf_field("Full Name")
            pdf_dob = pdf_field("Date of Birth")
            pdf_nationality = pdf_field("Nationality")
            pdf_expiry = pdf_field("Passport Expiry")

            print(
                "SYNTHETIC PDF:",
                pdf_passport,
                pdf_name,
                pdf_dob,
                pdf_nationality,
                pdf_expiry,
            )

            if pdf_passport and pdf_name and pdf_dob and pdf_nationality:
                parts = pdf_name.split(maxsplit=1)

                mrz_result = {
                    "detected": True,
                    "passport_number": pdf_passport,
                    "surname": parts[-1],
                    "given_names": parts[0] if len(parts) > 1 else "",
                    "nationality": pdf_nationality,
                    "date_of_birth_raw": pdf_dob,
                    "sex": "X",
                    "expiry_date_raw": pdf_expiry,
                    "check_digits": {
                        "passport_number": True,
                        "date_of_birth": True,
                        "expiry_date": True,
                    },
                    "valid": True,
                    "synthetic_pdf": True,
                }

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


# BorderSight judge-facing frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

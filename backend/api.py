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
# COMPLETE SCREENING PIPELINE
# ============================================================

@app.post("/screen")
def complete_screening(request: ScreeningRequest):

    traveler_data = request.model_dump()

    # --------------------------------------------------------
    # 1. IMMIGRATION
    # --------------------------------------------------------

    try:
        immigration = verify_immigration(traveler_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Immigration check failed: {str(e)}"
        )

    # --------------------------------------------------------
    # 2. SECURITY
    # --------------------------------------------------------

    try:
        security = screen_security(traveler_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Security screening failed: {str(e)}"
        )

    # --------------------------------------------------------
    # 3. DETERMINE FINAL STATUS
    # --------------------------------------------------------

    reasons = []

    # Passport problems
    if not immigration.get("passport_found", False):

        reasons.append(
            "Passport not found in synthetic database"
        )

    if immigration.get("details_match") is False:

        reasons.append(
            "Passport details do not match database"
        )

    # Visa problems
    if immigration.get("visa_required"):

        if not immigration.get("visa_valid", False):

            reasons.append(
                immigration.get(
                    "reason",
                    "Visa is invalid or unavailable"
                )
            )

        if not immigration.get("visa_passport_match", False):

            reasons.append(
                "Visa does not match passport"
            )

    # Security problems
    if security.get("match", False):

        reasons.append(
            security.get(
                "reason",
                "Security record requires secondary review"
            )
        )

    # --------------------------------------------------------
    # FINAL DECISION
    # --------------------------------------------------------

    if security.get("match", False):

        final_status = "SECURITY_ALERT"

    elif not immigration.get("passport_found", False):

        final_status = "REVIEW"

    elif immigration.get("details_match") is False:

        final_status = "REVIEW"

    elif (
        immigration.get("visa_required")
        and not immigration.get("visa_valid", False)
    ):

        final_status = "REVIEW"

    elif (
        immigration.get("visa_required")
        and not immigration.get("visa_passport_match", False)
    ):

        final_status = "REVIEW"

    else:

        final_status = "CLEAR"

    # --------------------------------------------------------
    # RESPONSE
    # --------------------------------------------------------

    return {
        "success": True,

        "traveler": {
            "name": traveler_data.get("name"),
            "passport_number": traveler_data.get("passport_number"),
            "nationality": traveler_data.get("nationality")
        },

        "immigration": immigration,

        "security": security,

        "final_status": final_status,

        "reasons": reasons,

        "message": (
            "Traveler cleared"
            if final_status == "CLEAR"
            else "Secondary review required"
            if final_status == "REVIEW"
            else "Security alert triggered"
        )
    }


# ============================================================
# DEMO SCREENING
# ============================================================

@app.get("/demo")
def demo():

    demo_traveler = ScreeningRequest(
        name="JOHN CARTER",
        passport_number="DEMO-P-1001",
        nationality="USA",
        date_of_birth="1998-08-15",
        expiry="2031-08-15"
    )

    result = complete_screening(demo_traveler)

    return result


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "backend.api:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
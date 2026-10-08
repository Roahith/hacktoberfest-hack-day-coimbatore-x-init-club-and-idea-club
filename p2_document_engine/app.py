from fastapi import FastAPI, File, UploadFile, HTTPException

from p2_document_engine.ocr_engine import (
    extract_document_text
)

from p2_document_engine.mrz_engine import (
    extract_mrz
)

from p2_document_engine.validation import (
    extract_passport_number_from_ocr,
    extract_date_of_birth,
    database_comparison,
    calculate_tamper_indicators
)


app = FastAPI(
    title="P2 Document Intelligence Engine",
    description="OCR, MRZ and document evidence analysis API",
    version="1.0.0"
)


ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
}


@app.get("/")
def root():

    return {
        "service": "P2 Document Intelligence Engine",
        "status": "running"
    }


@app.post("/analyze-document")
async def analyze_document(
    file: UploadFile = File(...)
):

    filename = file.filename or ""

    extension = ""

    if "." in filename:
        extension = "." + filename.rsplit(".", 1)[1].lower()

    if extension not in ALLOWED_EXTENSIONS:

        raise HTTPException(
            status_code=400,
            detail="Only PDF, PNG, JPG and JPEG files are supported."
        )

    file_bytes = await file.read()

    if not file_bytes:

        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    try:

        # -------------------------
        # STEP 1: OCR
        # -------------------------

        ocr_result = extract_document_text(
            file_bytes,
            filename
        )

        raw_text = ocr_result["raw_text"]

        # -------------------------
        # STEP 2: MRZ
        # -------------------------

        mrz_result = extract_mrz(
            raw_text
        )

        # -------------------------
        # STEP 3: Passport fields
        # -------------------------

        passport_number_ocr = (
            extract_passport_number_from_ocr(
                raw_text
            )
        )

        date_of_birth_ocr = (
            extract_date_of_birth(
                raw_text
            )
        )

        passport_data = {}

        if mrz_result.get("detected"):

            passport_data = {
                "passport_number": mrz_result.get(
                    "passport_number"
                ),
                "surname": mrz_result.get(
                    "surname"
                ),
                "given_names": mrz_result.get(
                    "given_names"
                ),
                "nationality": mrz_result.get(
                    "nationality"
                ),
                "date_of_birth": mrz_result.get(
                    "date_of_birth_raw"
                ),
                "sex": mrz_result.get(
                    "sex"
                ),
                "expiry_date": mrz_result.get(
                    "expiry_date_raw"
                )
            }

        # -------------------------
        # STEP 4: OCR ↔ MRZ
        # -------------------------

        ocr_mrz_match = None

        if mrz_result.get("detected"):

            matches = []

            if passport_number_ocr:

                matches.append(
                    passport_number_ocr.replace(
                        " ",
                        ""
                    ).upper()
                    ==
                    str(
                        mrz_result.get(
                            "passport_number",
                            ""
                        )
                    ).upper()
                )

            if date_of_birth_ocr:

                matches.append(
                    date_of_birth_ocr.replace(
                        "/",
                        ""
                    ).replace(
                        "-",
                        ""
                    )
                    ==
                    str(
                        mrz_result.get(
                            "date_of_birth_raw",
                            ""
                        )
                    )
                )

            if matches:

                ocr_mrz_match = all(matches)

        # -------------------------
        # STEP 5: Database
        # -------------------------

        # P3 will connect the synthetic database here.
        database_record = None

        database_result = database_comparison(
            passport_data,
            database_record
        )

        # -------------------------
        # STEP 6: Tamper evidence
        # -------------------------

        tamper_result = calculate_tamper_indicators(
            mrz_result,
            database_result
        )

        # -------------------------
        # FINAL JSON
        # -------------------------

        return {

            "document": {
                "filename": filename,
                "type": (
                    "passport"
                    if mrz_result.get("detected")
                    else "unknown"
                )
            },

            "ocr": {
                "status": "success",
                "confidence": ocr_result["confidence"],
                "pages": ocr_result["pages"],
                "raw_text": raw_text
            },

            "passport": passport_data,

            "mrz": {
                "detected": mrz_result.get(
                    "detected",
                    False
                ),
                "valid": mrz_result.get(
                    "valid",
                    False
                ),
                "check_digits": mrz_result.get(
                    "check_digits",
                    {}
                )
            },

            "consistency": {
                "ocr_mrz_match": ocr_mrz_match,
                "database_match": database_result.get(
                    "match"
                )
            },

            "tamper": tamper_result
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"Document analysis failed: {str(error)}"
        )
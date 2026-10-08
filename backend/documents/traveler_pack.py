from pathlib import Path
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.units import mm


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_ROOT = PROJECT_ROOT / "test_documents" / "travelers"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)


# ============================================================
# STYLES
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "TravelerTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=20,
    leading=24,
    spaceAfter=10,
)

WARNING_STYLE = ParagraphStyle(
    "Warning",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=10,
    leading=14,
    textColor=colors.red,
    spaceAfter=16,
)

NORMAL_STYLE = ParagraphStyle(
    "TravelerNormal",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
)

SECTION_STYLE = ParagraphStyle(
    "TravelerSection",
    parent=styles["Heading2"],
    fontSize=13,
    leading=16,
    spaceBefore=12,
    spaceAfter=8,
)


# ============================================================
# VALIDATION
# ============================================================

REQUIRED_FIELDS = [
    "name",
    "date_of_birth",
    "nationality",
    "passport_number",
    "passport_expiry",
]


def validate_traveler(traveler):
    """
    Validate the minimum traveler information required
    to generate a synthetic document pack.
    """

    if not isinstance(traveler, dict):
        raise TypeError("traveler must be a dictionary")

    missing = []

    for field in REQUIRED_FIELDS:
        value = traveler.get(field)

        if value is None or str(value).strip() == "":
            missing.append(field)

    if missing:
        raise ValueError(
            "Missing traveler fields: " + ", ".join(missing)
        )

    return True


# ============================================================
# SAFE DIRECTORY NAME
# ============================================================

def safe_name(value):
    """
    Convert a traveler name into a safe folder name.
    """

    value = str(value).strip()

    cleaned = "".join(
        character
        if character.isalnum() or character in ("-", "_")
        else "_"
        for character in value
    )

    return cleaned.upper() or "UNKNOWN_TRAVELER"


# ============================================================
# GENERIC PDF BUILDER
# ============================================================

def build_pdf(path, title, document_type, fields, notes):
    """
    Create one clearly synthetic PDF document.
    """

    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    story = []

    story.append(
        Paragraph(
            title,
            TITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "DEMO / SYNTHETIC DOCUMENT - NOT A REAL GOVERNMENT DOCUMENT",
            WARNING_STYLE,
        )
    )

    story.append(
        Paragraph(
            "<b>VERILENS AI HACKATHON DEMONSTRATION</b>",
            NORMAL_STYLE,
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"<b>Document Type:</b> {document_type}",
            NORMAL_STYLE,
        )
    )

    story.append(Spacer(1, 12))

    table_data = [
        ["FIELD", "VALUE"],
    ]

    for key, value in fields.items():
        table_data.append(
            [
                str(key),
                str(value),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            55 * mm,
            105 * mm,
        ],
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    colors.grey,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (0, -1),
                    "Helvetica-Bold",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    9,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(table)

    story.append(Spacer(1, 18))

    story.append(
        Paragraph(
            "DEMO VERIFICATION NOTES",
            SECTION_STYLE,
        )
    )

    for note in notes:
        story.append(
            Paragraph(
                f"• {note}",
                NORMAL_STYLE,
            )
        )

    story.append(Spacer(1, 25))

    story.append(
        Paragraph(
            "This document contains fictional data generated "
            "for software testing.",
            NORMAL_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It must not be used as an identity document.",
            NORMAL_STYLE,
        )
    )

    doc.build(story)

    return path


# ============================================================
# ORIGINAL PASSPORT
# ============================================================

def generate_original_passport(traveler, output_dir):
    """
    Generate a passport whose fields exactly match the
    fictional traveler profile.
    """

    path = output_dir / "original_passport.pdf"

    fields = {
        "Passport Number": traveler["passport_number"],
        "Full Name": traveler["name"],
        "Date of Birth": traveler["date_of_birth"],
        "Nationality": traveler["nationality"],
        "Passport Expiry": traveler["passport_expiry"],
        "Document Status": "VALID",
        "MRZ Status": "VALID",
    }

    notes = [
        "All fields match the fictional traveler profile.",
        "This document represents the normal CLEAR scenario.",
        "No real government document format is being reproduced.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC PASSPORT",
        "Passport",
        fields,
        notes,
    )


# ============================================================
# TAMPERED PASSPORT
# ============================================================

def generate_tampered_passport(traveler, output_dir):
    """
    Generate a passport where the displayed passport number
    intentionally differs from the expected number.
    """

    path = output_dir / "tampered_passport.pdf"

    tampered_number = (
        "TAMPERED-" + traveler["passport_number"]
    )

    fields = {
        "Passport Number": tampered_number,
        "Full Name": traveler["name"],
        "Date of Birth": traveler["date_of_birth"],
        "Nationality": traveler["nationality"],
        "Passport Expiry": traveler["passport_expiry"],
        "Visual Passport Number": tampered_number,
        "Expected Passport Number": traveler["passport_number"],
        "MRZ Status": "INCONSISTENT",
        "Document Status": "TAMPERED DEMO",
    }

    notes = [
        "Passport number has intentionally been modified.",
        "Expected database value does not match the document.",
        "This scenario should trigger document review.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC TAMPERED PASSPORT",
        "Passport - Tampering Test",
        fields,
        notes,
    )


# ============================================================
# DETAIL MISMATCH PASSPORT
# ============================================================

def generate_detail_mismatch_passport(traveler, output_dir):
    """
    Generate a passport with a deliberately incorrect DOB.
    """

    path = output_dir / "detail_mismatch_passport.pdf"

    fields = {
        "Passport Number": traveler["passport_number"],
        "Full Name": traveler["name"],
        "Date of Birth": "2000-01-01",
        "Expected Date of Birth": traveler["date_of_birth"],
        "Nationality": traveler["nationality"],
        "Passport Expiry": traveler["passport_expiry"],
        "Document Status": "DETAIL MISMATCH",
    }

    notes = [
        "Date of birth intentionally differs from the traveler profile.",
        "Passport number remains unchanged.",
        "This scenario should trigger secondary review.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC DETAIL-MISMATCH PASSPORT",
        "Passport - Field Mismatch Test",
        fields,
        notes,
    )


# ============================================================
# ORIGINAL VISA
# ============================================================

def generate_original_visa(traveler, output_dir):
    """
    Generate an active visa linked to the traveler passport.
    """

    path = output_dir / "original_visa.pdf"

    fields = {
        "Visa Number": "DEMO-V-" + traveler["passport_number"][-4:],
        "Applicant": traveler["name"],
        "Nationality": traveler["nationality"],
        "Passport Number": traveler["passport_number"],
        "Visa Type": "DEMO TOURIST VISA",
        "Valid From": "2026-01-01",
        "Valid Until": "2027-01-01",
        "Status": "ACTIVE",
    }

    notes = [
        "Visa is intentionally linked to the traveler passport.",
        "Visa status is ACTIVE.",
        "This represents the valid visa scenario.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC INDIA VISA",
        "Visa / ETA",
        fields,
        notes,
    )


# ============================================================
# EXPIRED VISA
# ============================================================

def generate_expired_visa(traveler, output_dir):
    """
    Generate an expired visa linked to the traveler passport.
    """

    path = output_dir / "expired_visa.pdf"

    fields = {
        "Visa Number": "DEMO-EXP-" + traveler["passport_number"][-4:],
        "Applicant": traveler["name"],
        "Nationality": traveler["nationality"],
        "Passport Number": traveler["passport_number"],
        "Visa Type": "DEMO TOURIST VISA",
        "Valid From": "2024-01-01",
        "Valid Until": "2025-01-01",
        "Status": "EXPIRED",
    }

    notes = [
        "Visa is intentionally expired.",
        "Passport association remains correct.",
        "This should produce a visa review result.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC EXPIRED INDIA VISA",
        "Visa / ETA - Expired Test",
        fields,
        notes,
    )


# ============================================================
# WRONG PASSPORT VISA
# ============================================================

def generate_wrong_passport_visa(traveler, output_dir):
    """
    Generate an active visa that belongs to another passport.
    """

    path = output_dir / "wrong_passport_visa.pdf"

    wrong_passport = (
        "DEMO-WRONG-" +
        traveler["passport_number"][-4:]
    )

    fields = {
        "Visa Number": "DEMO-WRONG-VISA",
        "Applicant": traveler["name"],
        "Nationality": traveler["nationality"],
        "Visa Passport Number": wrong_passport,
        "Presented Passport Number": traveler["passport_number"],
        "Visa Type": "DEMO TOURIST VISA",
        "Status": "ACTIVE",
    }

    notes = [
        "Visa is active but belongs to another passport number.",
        "Visa passport number intentionally differs from the traveler passport.",
        "This scenario should trigger immigration review.",
    ]

    return build_pdf(
        path,
        "SYNTHETIC WRONG-PASSPORT VISA",
        "Visa / ETA - Passport Mismatch Test",
        fields,
        notes,
    )


# ============================================================
# COMPLETE DOCUMENT PACK
# ============================================================

def generate_document_pack(traveler):
    """
    Generate all six synthetic documents for a traveler.

    Returns a dictionary that can later be returned directly
    from a FastAPI endpoint.
    """

    validate_traveler(traveler)

    folder_name = safe_name(traveler["name"])

    output_dir = OUTPUT_ROOT / folder_name

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    generated = {}

    generated["original_passport"] = str(
        generate_original_passport(
            traveler,
            output_dir,
        )
    )

    generated["tampered_passport"] = str(
        generate_tampered_passport(
            traveler,
            output_dir,
        )
    )

    generated["detail_mismatch_passport"] = str(
        generate_detail_mismatch_passport(
            traveler,
            output_dir,
        )
    )

    generated["original_visa"] = str(
        generate_original_visa(
            traveler,
            output_dir,
        )
    )

    generated["expired_visa"] = str(
        generate_expired_visa(
            traveler,
            output_dir,
        )
    )

    generated["wrong_passport_visa"] = str(
        generate_wrong_passport_visa(
            traveler,
            output_dir,
        )
    )

    return {
        "traveler": traveler,
        "folder": str(output_dir),
        "documents": generated,
        "document_count": len(generated),
    }


# ============================================================
# DEMO TEST
# ============================================================

if __name__ == "__main__":

    demo_traveler = {
        "name": "ARUN KUMAR",
        "date_of_birth": "1997-04-12",
        "nationality": "INDIA",
        "passport_number": "DEMO-P-2001",
        "passport_expiry": "2032-04-12",
    }

    print()
    print("=" * 70)
    print("VERILENS AI - DYNAMIC TRAVELER DOCUMENT PACK")
    print("=" * 70)

    result = generate_document_pack(
        demo_traveler
    )

    print()
    print("Traveler:")
    print(
        f"  Name: {result['traveler']['name']}"
    )
    print(
        f"  Passport: {result['traveler']['passport_number']}"
    )
    print(
        f"  Nationality: {result['traveler']['nationality']}"
    )

    print()
    print(
        f"Generated documents: {result['document_count']}"
    )

    print()

    for document_name, path in result["documents"].items():
        print(
            f"[CREATED] {document_name}: {path}"
        )

    print()
    print("=" * 70)
    print("DOCUMENT PACK GENERATION COMPLETE")
    print("=" * 70)
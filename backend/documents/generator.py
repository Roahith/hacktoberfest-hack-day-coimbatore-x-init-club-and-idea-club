from pathlib import Path
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
    PageBreak,
)
from reportlab.lib.units import mm


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "test_documents"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# COMMON STYLES
# ============================================================

styles = getSampleStyleSheet()

TITLE_STYLE = ParagraphStyle(
    "DemoTitle",
    parent=styles["Title"],
    alignment=TA_CENTER,
    fontSize=20,
    leading=24,
    spaceAfter=12,
)

SUBTITLE_STYLE = ParagraphStyle(
    "DemoSubtitle",
    parent=styles["Normal"],
    alignment=TA_CENTER,
    fontSize=10,
    leading=14,
    textColor=colors.red,
    spaceAfter=18,
)

SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Heading2"],
    fontSize=13,
    leading=16,
    spaceBefore=10,
    spaceAfter=8,
)

NORMAL_STYLE = ParagraphStyle(
    "NormalDemo",
    parent=styles["Normal"],
    fontSize=10,
    leading=14,
)


# ============================================================
# HELPERS
# ============================================================

def demo_header(story, title):
    """
    Adds a very obvious synthetic/demo warning.
    """

    story.append(Paragraph(title, TITLE_STYLE))

    story.append(
        Paragraph(
            "DEMO / SYNTHETIC DOCUMENT - NOT A REAL GOVERNMENT DOCUMENT",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "This document is generated exclusively for the VeriLens AI "
            "hackathon demonstration.",
            NORMAL_STYLE,
        )
    )

    story.append(Spacer(1, 12))


def make_table(data):
    """
    Creates a simple document information table.
    """

    table = Table(
        data,
        colWidths=[55 * mm, 105 * mm],
        repeatRows=1,
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 1), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )

    return table


def save_pdf(filename, title, document_type, fields, notes=None):
    """
    Generic synthetic PDF generator.
    """

    output_path = OUTPUT_DIR / filename

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    story = []

    demo_header(story, title)

    story.append(
        Paragraph(
            f"<b>Document type:</b> {document_type}",
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

    story.append(make_table(table_data))

    if notes:
        story.append(Spacer(1, 18))

        story.append(
            Paragraph(
                "VERIFICATION NOTES",
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
            "VeriLens AI Synthetic Test Document",
            NORMAL_STYLE,
        )
    )

    story.append(
        Paragraph(
            "For hackathon demonstration only.",
            NORMAL_STYLE,
        )
    )

    doc.build(story)

    return output_path


# ============================================================
# PASSPORT DOCUMENTS
# ============================================================

def generate_original_passport():
    return save_pdf(
        "original_passport.pdf",
        "SYNTHETIC PASSPORT",
        "Passport",
        {
            "Passport Number": "DEMO-P-1001",
            "Full Name": "JOHN CARTER",
            "Date of Birth": "1998-08-15",
            "Nationality": "USA",
            "Passport Expiry": "2031-08-15",
            "Document Status": "VALID",
            "MRZ Status": "VALID",
        },
        [
            "Passport details match the synthetic passport database.",
            "MRZ information is internally consistent.",
            "This document represents the CLEAR demonstration scenario.",
        ],
    )


def generate_tampered_passport():
    return save_pdf(
        "tampered_passport.pdf",
        "SYNTHETIC TAMPERED PASSPORT",
        "Passport - Tampering Scenario",
        {
            "Passport Number": "DEMO-P-9001",
            "Full Name": "JOHN CARTER",
            "Date of Birth": "1998-08-15",
            "Nationality": "USA",
            "Passport Expiry": "2031-08-15",
            "Visual Passport Number": "DEMO-P-9001",
            "MRZ Passport Number": "DEMO-P-1001",
            "Document Status": "INCONSISTENT",
        },
        [
            "Visual passport number intentionally differs from MRZ.",
            "Synthetic database expects DEMO-P-1001.",
            "This scenario should trigger document inconsistency review.",
        ],
    )


def generate_mismatch_passport():
    return save_pdf(
        "mismatch_passport.pdf",
        "SYNTHETIC DETAIL-MISMATCH PASSPORT",
        "Passport - Detail Mismatch Scenario",
        {
            "Passport Number": "DEMO-P-1001",
            "Full Name": "JOHN CARTER",
            "Date of Birth": "2000-01-01",
            "Nationality": "USA",
            "Passport Expiry": "2031-08-15",
            "Document Status": "DETAIL MISMATCH",
        },
        [
            "Synthetic database DOB is 1998-08-15.",
            "Document DOB is intentionally changed to 2000-01-01.",
            "This scenario should trigger secondary review.",
        ],
    )


# ============================================================
# VISA DOCUMENTS
# ============================================================

def generate_original_visa():
    return save_pdf(
        "original_visa.pdf",
        "SYNTHETIC INDIA VISA",
        "Visa / ETA",
        {
            "Visa Number": "DEMO-V-1001",
            "Passport Number": "DEMO-P-1001",
            "Applicant": "JOHN CARTER",
            "Nationality": "USA",
            "Visa Type": "DEMO TOURIST VISA",
            "Valid From": "2026-01-01",
            "Valid Until": "2027-01-01",
            "Status": "ACTIVE",
        },
        [
            "Visa belongs to DEMO-P-1001.",
            "Visa status is ACTIVE.",
            "Visa is valid for the demonstration date.",
        ],
    )


def generate_expired_visa():
    return save_pdf(
        "expired_visa.pdf",
        "SYNTHETIC EXPIRED INDIA VISA",
        "Visa / ETA - Expired Scenario",
        {
            "Visa Number": "DEMO-V-1002",
            "Passport Number": "DEMO-P-1002",
            "Applicant": "EMILY JOHNSON",
            "Nationality": "USA",
            "Visa Type": "DEMO TOURIST VISA",
            "Valid From": "2024-01-01",
            "Valid Until": "2025-01-01",
            "Status": "EXPIRED",
        },
        [
            "Visa is intentionally expired.",
            "This scenario should trigger immigration review.",
        ],
    )


def generate_wrong_passport_visa():
    return save_pdf(
        "wrong_passport_visa.pdf",
        "SYNTHETIC WRONG-PASSPORT VISA",
        "Visa / ETA - Passport Mismatch Scenario",
        {
            "Visa Number": "DEMO-V-9001",
            "Visa Applicant": "JOHN CARTER",
            "Visa Passport Number": "DEMO-P-9999",
            "Presented Passport Number": "DEMO-P-1001",
            "Nationality": "USA",
            "Status": "ACTIVE",
        },
        [
            "Visa is active but belongs to another passport number.",
            "Visa passport number intentionally differs from presented passport.",
            "This scenario should trigger secondary immigration review.",
        ],
    )


# ============================================================
# GENERATE ALL DOCUMENTS
# ============================================================

def generate_all_documents():
    """
    Generate the complete synthetic document pack.
    """

    generated = []

    generated.append(generate_original_passport())
    generated.append(generate_tampered_passport())
    generated.append(generate_mismatch_passport())

    generated.append(generate_original_visa())
    generated.append(generate_expired_visa())
    generated.append(generate_wrong_passport_visa())

    return generated


# ============================================================
# COMMAND LINE ENTRY POINT
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 65)
    print("VERILENS AI - SYNTHETIC DOCUMENT GENERATOR")
    print("=" * 65)

    documents = generate_all_documents()

    print()

    for document in documents:
        print(f"[CREATED] {document}")

    print()
    print("=" * 65)
    print(f"Generated {len(documents)} synthetic documents.")
    print(f"Output directory: {OUTPUT_DIR}")
    print("=" * 65)
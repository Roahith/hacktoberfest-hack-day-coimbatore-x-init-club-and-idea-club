import io
import os
import re

import fitz
import pytesseract

from PIL import Image, ImageEnhance, ImageFilter


# Tell Python where Tesseract is installed on Windows
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if os.path.exists(TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def pdf_to_images(file_bytes: bytes):
    """Convert every PDF page into a PIL image."""

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    images = []

    for page in document:
        matrix = fitz.Matrix(2.5, 2.5)

        pixmap = page.get_pixmap(
            matrix=matrix,
            alpha=False
        )

        image = Image.open(
            io.BytesIO(
                pixmap.tobytes("png")
            )
        )

        images.append(image)

    document.close()

    return images


def extract_pdf_text_layer(file_bytes: bytes):
    """
    Extract text directly from a PDF text layer.

    This is useful when a PDF contains selectable text.
    Scanned PDFs may return little or no text.
    """

    document = fitz.open(
        stream=file_bytes,
        filetype="pdf"
    )

    pages = []

    for page in document:
        text = page.get_text("text")
        pages.append(text)

    document.close()

    return "\n".join(pages)


def preprocess_image(image: Image.Image):
    """Improve image quality before normal OCR."""

    image = image.convert("RGB")

    width, height = image.size

    image = image.resize(
        (width * 2, height * 2)
    )

    image = image.convert("L")

    image = ImageEnhance.Contrast(
        image
    ).enhance(1.5)

    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


def extract_text_from_image(image: Image.Image):
    """Run the normal OCR pass."""

    processed_image = preprocess_image(
        image
    )

    data = pytesseract.image_to_data(
        processed_image,
        config="--psm 6",
        output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []

    for i, word in enumerate(
        data["text"]
    ):

        word = word.strip()

        if not word:
            continue

        words.append(word)

        try:
            confidence = float(
                data["conf"][i]
            )

            if confidence >= 0:
                confidences.append(
                    confidence
                )

        except (ValueError, TypeError):
            pass

    raw_text = " ".join(words)

    if confidences:

        average_confidence = (
            sum(confidences)
            / len(confidences)
            / 100
        )

    else:

        average_confidence = 0.0

    return (
        raw_text,
        average_confidence
    )


def extract_mrz_text_from_image(
    image: Image.Image
):
    """
    Dedicated MRZ OCR fallback.

    Runs several OCR layouts over the lower
    portion of the document.
    """

    image = image.convert("RGB")

    width, height = image.size

    # Use the lower 45% rather than an extremely
    # narrow crop.
    crop_top = int(height * 0.55)

    mrz_region = image.crop(
        (
            0,
            crop_top,
            width,
            height
        )
    )

    mrz_region = mrz_region.resize(
        (
            mrz_region.width * 3,
            mrz_region.height * 3
        )
    )

    mrz_region = mrz_region.convert("L")

    mrz_region = ImageEnhance.Contrast(
        mrz_region
    ).enhance(2.0)

    mrz_region = mrz_region.filter(
        ImageFilter.SHARPEN
    )

    results = []

    for psm in [6, 11, 12, 13]:

        text = pytesseract.image_to_string(
            mrz_region,
            config=f"--psm {psm}"
        )

        if text.strip():
            results.append(
                text.strip()
            )

    return "\n".join(results)


def looks_like_mrz(text: str):
    """
    Check whether text contains something that
    resembles passport MRZ lines.
    """

    if not text:
        return False

    lines = [
        re.sub(
            r"\s+",
            "",
            line.upper()
        )
        for line in text.splitlines()
    ]

    candidates = [
        line
        for line in lines
        if len(line) >= 30
    ]

    return len(candidates) >= 2


def extract_document_text(
    file_bytes: bytes,
    filename: str
):
    """
    Extract normal OCR plus MRZ information.

    For text PDFs, the embedded text layer is preferred
    for MRZ extraction.

    For scanned PDFs/images, MRZ OCR is used as fallback.
    """

    extension = os.path.splitext(
        filename
    )[1].lower()

    pdf_text = ""

    if extension == ".pdf":

        pdf_text = extract_pdf_text_layer(
            file_bytes
        )

        images = pdf_to_images(
            file_bytes
        )

    elif extension in [
        ".png",
        ".jpg",
        ".jpeg"
    ]:

        image = Image.open(
            io.BytesIO(file_bytes)
        )

        images = [image]

    else:

        raise ValueError(
            "Unsupported file type"
        )

    all_text = []
    all_mrz_text = []
    page_confidences = []

    for image in images:

        text, confidence = (
            extract_text_from_image(
                image
            )
        )

        mrz_text = (
            extract_mrz_text_from_image(
                image
            )
        )

        all_text.append(text)
        all_mrz_text.append(mrz_text)

        page_confidences.append(
            confidence
        )

    raw_text = "\n".join(
        all_text
    )

    # ---------------------------------
    # MRZ source selection
    # ---------------------------------

    if looks_like_mrz(pdf_text):

        dedicated_mrz_text = pdf_text

    else:

        dedicated_mrz_text = "\n".join(
            all_mrz_text
        )

    # ---------------------------------
    # Confidence
    # ---------------------------------

    if page_confidences:

        overall_confidence = (
            sum(page_confidences)
            / len(page_confidences)
        )

    else:

        overall_confidence = 0.0

    return {
        "raw_text": raw_text,

        "mrz_text": dedicated_mrz_text,

        "pdf_text": pdf_text,

        "confidence": round(
            overall_confidence,
            3
        ),

        "pages": len(images)
    }


def normalize_text(text: str):
    """Normalize OCR text for comparisons."""

    text = text.upper()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()
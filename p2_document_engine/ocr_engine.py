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
            io.BytesIO(pixmap.tobytes("png"))
        )

        images.append(image)

    document.close()

    return images


def preprocess_image(image: Image.Image):
    """Improve image quality before OCR."""

    image = image.convert("RGB")

    # Increase resolution
    width, height = image.size

    image = image.resize(
        (width * 2, height * 2)
    )

    # Convert to grayscale
    image = image.convert("L")

    # Improve contrast
    image = ImageEnhance.Contrast(image).enhance(1.5)

    # Sharpen text
    image = image.filter(
        ImageFilter.SHARPEN
    )

    return image


def extract_text_from_image(image: Image.Image):
    """Run Tesseract OCR on one image."""

    processed_image = preprocess_image(image)

    data = pytesseract.image_to_data(
        processed_image,
        config="--psm 6",
        output_type=pytesseract.Output.DICT
    )

    words = []
    confidences = []

    for i, word in enumerate(data["text"]):

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

    return raw_text, average_confidence


def extract_document_text(
    file_bytes: bytes,
    filename: str
):
    """Extract OCR text from PDF or image."""

    extension = os.path.splitext(
        filename
    )[1].lower()

    if extension == ".pdf":

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
    page_confidences = []

    for image in images:

        text, confidence = (
            extract_text_from_image(image)
        )

        all_text.append(text)
        page_confidences.append(
            confidence
        )

    raw_text = "\n".join(
        all_text
    )

    if page_confidences:
        overall_confidence = (
            sum(page_confidences)
            / len(page_confidences)
        )
    else:
        overall_confidence = 0.0

    return {
        "raw_text": raw_text,
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
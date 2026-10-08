from pathlib import Path
import cv2
import numpy as np

BASE = Path(__file__).resolve().parents[2]
MODELS = BASE / "models"
FACES = BASE / "data" / "faces"

_detector = cv2.FaceDetectorYN.create(
    str(MODELS / "face_detection_yunet_2023mar.onnx"),
    "",
    (320, 320),
)

_recognizer = cv2.FaceRecognizerSF.create(
    str(MODELS / "face_recognition_sface_2021dec.onnx"),
    "",
)


def _feature(image):
    h, w = image.shape[:2]
    _detector.setInputSize((w, h))

    _, faces = _detector.detect(image)

    if faces is None or len(faces) == 0:
        raise ValueError("No face detected")

    face = faces[0]
    aligned = _recognizer.alignCrop(image, face)
    return _recognizer.feature(aligned)


def save_reference(passport: str, image_bytes: bytes):
    FACES.mkdir(parents=True, exist_ok=True)

    image = cv2.imdecode(
        np.frombuffer(image_bytes, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )

    if image is None:
        raise ValueError("Invalid image")

    _feature(image)

    path = FACES / f"{passport}.jpg"
    cv2.imwrite(str(path), image)

    return str(path)


def compare(passport: str, image_bytes: bytes):
    path = FACES / f"{passport}.jpg"

    if not path.exists():
        return {
            "checked": False,
            "match": False,
            "similarity": None,
            "reason": "No registered reference face found",
        }

    reference = cv2.imread(str(path))

    live = cv2.imdecode(
        np.frombuffer(image_bytes, dtype=np.uint8),
        cv2.IMREAD_COLOR,
    )

    if live is None:
        raise ValueError("Invalid live image")

    ref_feature = _feature(reference)
    live_feature = _feature(live)

    similarity = float(
        _recognizer.match(
            ref_feature,
            live_feature,
            cv2.FaceRecognizerSF_FR_COSINE,
        )
    )

    return {
        "checked": True,
        "match": similarity >= 0.363,
        "similarity": round(similarity, 4),
        "reason": None,
    }

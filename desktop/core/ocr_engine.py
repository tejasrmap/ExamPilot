"""
ExamPilot OCR Engine Module
Uses RapidOCR (PaddleOCR ONNX weights) for fast, highly accurate local OCR.
GT InnoX LLP
"""

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
from typing import List, Dict, Any, Tuple, Optional
import cv2

from desktop.utils.logger import logger

class OCREngine:
    """Production OCR Engine wrapper with preprocessing and confidence metrics."""

    def __init__(self):
        self._engine = None
        self._init_error = None
        self._init_engine()

    def _init_engine(self):
        # 1. Check OpenCV availability
        try:
            import cv2
        except ImportError:
            self._init_error = (
                "OpenCV dependency is missing. "
                "Please run: pip install opencv-python"
            )
            logger.error(self._init_error)
            return

        # 2. Check ONNX Runtime & RapidOCR availability
        try:
            import onnxruntime
        except ImportError:
            self._init_error = (
                "ONNX Runtime dependency is missing. "
                "Please run: pip install onnxruntime"
            )
            logger.error(self._init_error)
            return

        try:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
            self._init_error = None
            logger.info("RapidOCR (PaddleOCR ONNX) engine initialized successfully.")
        except ImportError as e:
            self._init_error = (
                f"RapidOCR dependency is missing: {e}. "
                "Please run: pip install rapidocr-onnxruntime onnxruntime"
            )
            logger.error(self._init_error)
            self._engine = None
        except Exception as e:
            self._init_error = (
                f"Failed to initialize RapidOCR engine models: {e}. "
                "Please verify Microsoft Visual C++ 2015-2022 Redistributable is installed."
            )
            logger.error(self._init_error, exc_info=True)
            self._engine = None

    def is_available(self) -> bool:
        return self._engine is not None

    def get_status_message(self) -> str:
        if self.is_available():
            return "Active (RapidOCR / PaddleOCR ONNX)"
        return self._init_error or "OCR engine not available."

    def preprocess_image(self, pil_img: Image.Image) -> np.ndarray:
        """
        Enhance image contrast, sharpness, and handle poor image resolution.
        """
        # Convert to RGB if palette or grayscale
        if pil_img.mode != "RGB":
            pil_img = pil_img.convert("RGB")

        # Upscale small images for clearer text detection
        w, h = pil_img.size
        if w < 600:
            scale = 600 / w
            pil_img = pil_img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        # Enhance contrast and sharpness
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced = enhancer.enhance(1.4)
        sharpener = ImageEnhance.Sharpness(enhanced)
        sharpened = sharpener.enhance(1.3)

        # Convert to numpy OpenCV BGR format
        cv_img = cv2.cvtColor(np.array(sharpened), cv2.COLOR_RGB2BGR)

        # Subtle denoising
        cv_img = cv2.fastNlMeansDenoisingColored(cv_img, None, 4, 4, 7, 21)
        return cv_img

    def extract_text(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text lines with bounding boxes and confidence scores.
        Returns:
            {
                "success": bool,
                "lines": List[Dict[str, Any]],  # each: {"text": str, "confidence": float, "box": list}
                "full_text": str,
                "avg_confidence": float,
                "error": Optional[str]
            }
        """
        if not self._engine:
            self._init_engine()

        if not self._engine:
            return {
                "success": False,
                "lines": [],
                "full_text": "",
                "avg_confidence": 0.0,
                "error": self._init_error or "OCR engine not available. Please install dependencies."
            }

        try:
            prep_img = self.preprocess_image(image)
            result, _ = self._engine(prep_img)

            if not result:
                logger.warning("OCR detected no text elements in image.")
                return {
                    "success": True,
                    "lines": [],
                    "full_text": "",
                    "avg_confidence": 0.0,
                    "error": None
                }

            extracted_lines = []
            confidences = []

            for item in result:
                box, text, score = item
                text_clean = str(text).strip()
                score_flt = float(score) if score is not None else 0.0
                if text_clean:
                    extracted_lines.append({
                        "text": text_clean,
                        "confidence": round(score_flt, 3),
                        "box": box
                    })
                    confidences.append(score_flt)

            # Sort lines top-to-bottom, left-to-right based on bounding box coordinates
            if extracted_lines:
                extracted_lines.sort(key=lambda it: (min(p[1] for p in it["box"]) // 12, min(p[0] for p in it["box"])))

            avg_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
            full_text = "\n".join([line["text"] for line in extracted_lines])

            logger.info(f"OCR extracted {len(extracted_lines)} lines with avg confidence {avg_conf}")
            return {
                "success": True,
                "lines": extracted_lines,
                "full_text": full_text,
                "avg_confidence": avg_conf,
                "error": None
            }

        except Exception as e:
            logger.error(f"Error during OCR processing: {e}", exc_info=True)
            return {
                "success": False,
                "lines": [],
                "full_text": "",
                "avg_confidence": 0.0,
                "error": str(e)
            }

ocr_engine = OCREngine()


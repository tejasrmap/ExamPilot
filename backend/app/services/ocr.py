"""
ExamPilot 2.0 Backend OCR & PDF Processing Service
Preserves RapidOCR (PaddleOCR ONNX) spatial pipeline and integrates PyMuPDF.
GT InnoX LLP
"""

import io
import logging
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import cv2

logger = logging.getLogger("exampilot.ocr")

class OCREngine:
    def __init__(self):
        self._engine = None
        self._init_error = None
        self._init_engine()

    def _init_engine(self):
        try:
            from rapidocr_onnxruntime import RapidOCR
            self._engine = RapidOCR()
            self._init_error = None
            logger.info("RapidOCR (PaddleOCR ONNX) engine initialized successfully in backend.")
        except Exception as e:
            self._init_error = f"RapidOCR initialization failed: {str(e)}"
            logger.error(self._init_error)

    def is_ready(self) -> bool:
        return self._engine is not None

    def get_error(self) -> Optional[str]:
        return self._init_error

    def preprocess_image(self, img: Image.Image) -> Image.Image:
        """
        Enhance image quality before OCR using Lanczos upscaling, contrast, and sharpening.
        """
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        # If low resolution, upscale using high-quality Lanczos resampling
        if w < 1000 or h < 600:
            scale = min(2.0, max(1200 / max(w, 1), 800 / max(h, 1)))
            img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)

        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)

        sharpener = ImageEnhance.Sharpness(img)
        img = sharpener.enhance(1.4)

        return img

    def extract_from_image(self, img: Image.Image) -> Dict[str, Any]:
        """
        Runs RapidOCR on a PIL Image, sorts bounding boxes by reading order (Y // 12, X),
        and returns clean text, average confidence, and line segments.
        """
        if not self.is_ready():
            return {
                "text": "",
                "confidence": 0.0,
                "lines": [],
                "error": self._init_error or "OCR Engine unavailable"
            }

        processed = self.preprocess_image(img)
        np_img = np.array(processed)
        # Convert RGB to BGR for cv2 / RapidOCR
        np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

        result, elapse_list = self._engine(np_img)
        if not result:
            return {
                "text": "",
                "confidence": 0.0,
                "lines": [],
                "error": None
            }

        # Spatial sorting: bucket by row height (Y // 12) then X coordinate
        boxes_with_text = []
        confidences = []
        for item in result:
            box, text, score = item[0], item[1], float(item[2])
            y_min = min(pt[1] for pt in box)
            x_min = min(pt[0] for pt in box)
            boxes_with_text.append({
                "y": y_min,
                "x": x_min,
                "bucket_y": int(y_min // 12),
                "text": text.strip(),
                "score": score,
                "box": box
            })
            confidences.append(score)

        # Sort top-to-bottom, left-to-right
        boxes_with_text.sort(key=lambda b: (b["bucket_y"], b["x"]))

        sorted_lines = [b["text"] for b in boxes_with_text if b["text"]]
        combined_text = "\n".join(sorted_lines)
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0

        return {
            "text": combined_text,
            "confidence": round(avg_confidence, 4),
            "lines": sorted_lines,
            "raw_boxes": boxes_with_text,
            "error": None
        }

    def extract_from_bytes(self, image_bytes: bytes) -> Dict[str, Any]:
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return self.extract_from_image(img)
        except Exception as e:
            return {
                "text": "",
                "confidence": 0.0,
                "lines": [],
                "error": f"Failed to parse image bytes: {str(e)}"
            }

    def extract_from_pdf_bytes(self, pdf_bytes: bytes, max_pages: int = 25) -> Dict[str, Any]:
        """
        Renders PDF pages using PyMuPDF (fitz) and runs OCR / text extraction on each page.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            return {"error": "PyMuPDF (fitz) is not installed", "pages": []}

        try:
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages)
            pages_data = []

            for page_idx in range(pages_to_process):
                page = doc.load_page(page_idx)
                # First check if PDF has native digital text
                native_text = page.get_text().strip()

                if len(native_text) > 80:
                    pages_data.append({
                        "page_number": page_idx + 1,
                        "text": native_text,
                        "extraction_method": "digital_pdf",
                        "confidence": 1.0,
                        "lines": [line.strip() for line in native_text.splitlines() if line.strip()]
                    })
                else:
                    # Scanned page: render to image at 200 DPI (zoom 2.08)
                    pix = page.get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    ocr_res = self.extract_from_image(img)
                    pages_data.append({
                        "page_number": page_idx + 1,
                        "text": ocr_res["text"],
                        "extraction_method": "rapidocr_scanned",
                        "confidence": ocr_res["confidence"],
                        "lines": ocr_res["lines"]
                    })

            full_text = "\n\n--- PAGE BREAK ---\n\n".join([p["text"] for p in pages_data])
            return {
                "total_pages": total_pages,
                "processed_pages": pages_to_process,
                "pages": pages_data,
                "full_text": full_text,
                "error": None
            }
        except Exception as e:
            return {
                "total_pages": 0,
                "processed_pages": 0,
                "pages": [],
                "full_text": "",
                "error": f"Failed to process PDF: {str(e)}"
            }

# Global singleton OCR engine instance
ocr_engine = OCREngine()


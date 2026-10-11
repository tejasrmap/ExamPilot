"""
ExamPilot Screen Capture Module
GT InnoX LLP — Understand Questions. Learn the Answers.
"""

import io
from typing import Optional, Tuple, Dict, Any
from PIL import Image
import mss
import mss.tools
from PySide6.QtCore import Qt, QRect, QPoint, Signal, QObject, QBuffer
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QCursor, QRegion

from desktop.utils.logger import logger
from desktop.config import COLORS

class ScreenCapture:
    """Handles high-performance multi-monitor screen capture using MSS."""

    def __init__(self):
        self._sct = mss.mss()

    def get_virtual_desktop_bounds(self) -> Dict[str, int]:
        """Get the bounding rect spanning all connected displays."""
        # Monitor 0 in MSS is all monitors combined
        mon0 = self._sct.monitors[0]
        return {
            "left": mon0["left"],
            "top": mon0["top"],
            "width": mon0["width"],
            "height": mon0["height"]
        }

    def capture_full_desktop(self) -> Image.Image:
        """Capture all monitors into a single PIL Image."""
        mon0 = self._sct.monitors[0]
        sct_img = self._sct.grab(mon0)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

    def capture_region(self, left: int, top: int, width: int, height: int) -> Optional[Image.Image]:
        """Capture a specific bounding box."""
        if width <= 0 or height <= 0:
            return None
        bounding_box = {"left": int(left), "top": int(top), "width": int(width), "height": int(height)}
        sct_img = self._sct.grab(bounding_box)
        return Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

class SnippetOverlayWidget(QWidget):
    """
    Full-screen transparent overlay for interactive region selection.
    User drags a box around the practice question.
    """
    snippet_captured = Signal(object)  # Emits PIL.Image
    snippet_cancelled = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))

        self.origin = QPoint()
        self.current = QPoint()
        self.is_selecting = False
        self.capture_tool = ScreenCapture()
        self.desktop_image: Optional[Image.Image] = None
        self.desktop_pixmap: Optional[QPixmap] = None

    def start_selection(self):
        """Pre-captures desktop on active screen, displays fullscreen overlay."""
        try:
            screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
            if screen:
                self.setGeometry(screen.geometry())
                self.desktop_pixmap = screen.grabWindow(0)
            else:
                self.desktop_pixmap = None

            self.origin = QPoint()
            self.current = QPoint()
            self.is_selecting = False
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
        except Exception as e:
            logger.error(f"Error starting region selection: {e}", exc_info=True)
            self.snippet_cancelled.emit()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw full desktop preview 1:1
        if self.desktop_pixmap:
            painter.drawPixmap(0, 0, self.desktop_pixmap)

        dark_overlay = QColor(11, 16, 32, 160)

        if self.is_selecting:
            selection_rect = QRect(self.origin, self.current).normalized()
            
            # Punch a hole in the dim overlay to reveal the exact un-dimmed screen underneath
            if selection_rect.isValid() and selection_rect.width() > 0 and selection_rect.height() > 0:
                dim_region = QRegion(self.rect()).subtracted(QRegion(selection_rect))
                painter.setClipRegion(dim_region)
                painter.fillRect(self.rect(), dark_overlay)
                painter.setClipping(False)
            else:
                painter.fillRect(self.rect(), dark_overlay)

            # Draw accent border
            pen = QPen(QColor(COLORS["accent_secondary"]), 2, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(selection_rect)

            # Dimensions badge
            w, h = selection_rect.width(), selection_rect.height()
            dim_text = f"{w} × {h} px"
            painter.setFont(QFont("Segoe UI", 9, QFont.Weight.DemiBold))
            painter.setPen(QColor(COLORS["text_primary"]))
            painter.setBrush(QColor(17, 24, 39, 220))
            badge_rect = QRect(selection_rect.left(), max(0, selection_rect.top() - 24), 90, 20)
            painter.drawRoundedRect(badge_rect, 4, 4)
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, dim_text)
        else:
            painter.fillRect(self.rect(), dark_overlay)
            # Helper guidance banner at top
            painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            painter.setPen(QColor(COLORS["text_primary"]))
            painter.setBrush(QColor(17, 24, 39, 230))
            guide_rect = QRect(self.width() // 2 - 220, 40, 440, 44)
            painter.drawRoundedRect(guide_rect, 8, 8)
            painter.setPen(QColor(COLORS["accent_secondary"]))
            painter.drawText(guide_rect, Qt.AlignmentFlag.AlignCenter, "Drag region around practice question • Esc to cancel")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.origin = event.pos()
            self.current = self.origin
            self.is_selecting = True
            self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.current = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.is_selecting = False
            rect = QRect(self.origin, event.pos()).normalized()
            self.hide()

            if rect.width() > 10 and rect.height() > 10 and self.desktop_pixmap:
                dpr = self.desktop_pixmap.devicePixelRatio()
                if dpr <= 0:
                    dpr = 1.0

                crop_x = int(rect.left() * dpr)
                crop_y = int(rect.top() * dpr)
                crop_w = int(rect.width() * dpr)
                crop_h = int(rect.height() * dpr)

                pw = self.desktop_pixmap.width()
                ph = self.desktop_pixmap.height()
                crop_x = max(0, min(pw - 1, crop_x))
                crop_y = max(0, min(ph - 1, crop_y))
                crop_w = max(1, min(pw - crop_x, crop_w))
                crop_h = max(1, min(ph - crop_y, crop_h))

                phys_rect = QRect(crop_x, crop_y, crop_w, crop_h)
                cropped_pixmap = self.desktop_pixmap.copy(phys_rect)

                buffer = QBuffer()
                buffer.open(QBuffer.OpenModeFlag.ReadWrite)
                cropped_pixmap.save(buffer, "PNG")
                cropped_pil = Image.open(io.BytesIO(bytes(buffer.data())))

                logger.info(f"Screen region captured: {cropped_pil.width}x{cropped_pil.height} px (logical {rect.width()}x{rect.height()} px, DPR {dpr:.2f})")
                self.snippet_captured.emit(cropped_pil)
            else:
                logger.warning("Selected region was too small (< 10px) or invalid, cancelled.")
                self.snippet_cancelled.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.is_selecting = False
            self.hide()
            self.snippet_cancelled.emit()

class HotkeyListener(QObject):
    """Global hotkey listener using pynput for non-intrusive capture activation."""
    hotkey_triggered = Signal()

    def __init__(self):
        super().__init__()
        self._listener = None
        self._is_running = False

    def start(self):
        try:
            from pynput import keyboard

            def on_activate():
                logger.info("Global capture hotkey (Ctrl+Shift+Q) triggered.")
                self.hotkey_triggered.emit()

            # Global hotkey Ctrl+Shift+Q
            self._listener = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+q': on_activate,
                '<ctrl>+<shift>+Q': on_activate
            })
            self._listener.daemon = True
            self._listener.start()
            self._is_running = True
            logger.info("Global hotkey listener active (Ctrl+Shift+Q).")
        except Exception as e:
            logger.warning(f"Could not register global hotkey (might be reserved): {e}")

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
            self._is_running = False

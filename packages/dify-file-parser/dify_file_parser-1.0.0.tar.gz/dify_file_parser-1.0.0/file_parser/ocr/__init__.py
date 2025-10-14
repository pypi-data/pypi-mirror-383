"""
OCR 模块
支持 Tesseract OCR 引擎
"""

from .tesseract_ocr import TesseractOCR
from .base_ocr import BaseOCR
from .ocr_manager import OCRManager

__all__ = ['TesseractOCR', 'BaseOCR', 'OCRManager']
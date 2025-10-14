"""
PDF 文件解析器
支持文本提取和 OCR 识别
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import io

from ..base import BaseParser, ParseResult, FileType
from ..ocr.ocr_manager import OCRManager


class PDFParser(BaseParser):
    """PDF 文件解析器"""
    
    def __init__(self):
        super().__init__()
        self.ocr_manager = OCRManager()
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".pdf"]
    
    @property
    def file_type(self) -> FileType:
        return FileType.PDF
    
    async def parse(self, file_path: Path) -> ParseResult:
        """
        解析 PDF 文件
        
        Args:
            file_path: PDF 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            # 首先尝试使用 pdfplumber 提取文本
            text_content = await self._extract_text_with_pdfplumber(file_path)
            
            # 如果文本内容较少，尝试使用 PyMuPDF 提取
            if len(text_content.strip()) < 100:
                text_content = await self._extract_text_with_pymupdf(file_path)
            
            # 如果仍然没有足够文本，尝试 OCR
            if len(text_content.strip()) < 50:
                ocr_text = await self._extract_text_with_ocr(file_path)
                if ocr_text:
                    text_content += f"\n\n{ocr_text}"
            
            # 获取页面信息
            page_count = await self._get_page_count(file_path)
            
            metadata = self._get_file_metadata(file_path)
            metadata.update({
                "page_count": page_count,
                "extraction_method": "pdfplumber + pymupdf + ocr",
                "has_ocr_content": len(ocr_text) > 0 if 'ocr_text' in locals() else False
            })
            
            return ParseResult(
                filename=Path(file_path).name,
                file_type=self.file_type,
                text=text_content.strip(),
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"PDF 解析失败: {str(e)}")
            raise
    
    async def _extract_text_with_pdfplumber(self, file_path: Path) -> str:
        """使用 pdfplumber 提取文本"""
        def _extract():
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(f"=== 第 {page_num} 页 ===\n{page_text}")
                    except Exception as e:
                        self.logger.warning(f"提取第 {page_num} 页失败: {str(e)}")
            return "\n\n".join(text_parts)
        
        return await asyncio.get_event_loop().run_in_executor(None, _extract)
    
    async def _extract_text_with_pymupdf(self, file_path: Path) -> str:
        """使用 PyMuPDF 提取文本"""
        def _extract():
            text_parts = []
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                try:
                    page = doc[page_num]
                    page_text = page.get_text()
                    if page_text.strip():
                        text_parts.append(f"=== 第 {page_num + 1} 页 ===\n{page_text}")
                except Exception as e:
                    self.logger.warning(f"PyMuPDF 提取第 {page_num + 1} 页失败: {str(e)}")
            doc.close()
            return "\n\n".join(text_parts)
        
        return await asyncio.get_event_loop().run_in_executor(None, _extract)
    
    async def _extract_text_with_ocr(self, file_path: Path) -> str:
        """使用 OCR 提取文本"""
        def _extract():
            try:
                doc = fitz.open(file_path)
                ocr_texts = []
                
                for page_num in range(min(doc.page_count, 5)):  # 限制 OCR 页面数量
                    try:
                        page = doc[page_num]
                        # 将页面转换为图片
                        mat = fitz.Matrix(2.0, 2.0)  # 提高分辨率
                        pix = page.get_pixmap(matrix=mat)
                        img_data = pix.tobytes("png")
                        
                        # 使用 OCR 识别
                        image = Image.open(io.BytesIO(img_data))
                        ocr_result = self.ocr_manager.extract_text_with_confidence(image)
                        
                        if ocr_result.get("text", "").strip():
                            # 生成置信度提示
                            confidence = ocr_result.get("confidence", 0)
                            
                            ocr_texts.append(f"=== 第 {page_num + 1} 页 OCR ===\n{ocr_result.get('text', '')}")
                            
                    except Exception as e:
                        self.logger.warning(f"OCR 处理第 {page_num + 1} 页失败: {str(e)}")
                
                doc.close()
                
                # 组合结果
                result = "\n\n".join(ocr_texts)
                
                return result
                
            except Exception as e:
                self.logger.error(f"OCR 处理失败: {str(e)}")
                return ""
        
        return await asyncio.get_event_loop().run_in_executor(None, _extract)
    
    async def _get_page_count(self, file_path: Path) -> int:
        """获取 PDF 页数"""
        def _get_count():
            try:
                with pdfplumber.open(file_path) as pdf:
                    return len(pdf.pages)
            except:
                try:
                    doc = fitz.open(file_path)
                    count = doc.page_count
                    doc.close()
                    return count
                except:
                    return 0
        
        return await asyncio.get_event_loop().run_in_executor(None, _get_count)

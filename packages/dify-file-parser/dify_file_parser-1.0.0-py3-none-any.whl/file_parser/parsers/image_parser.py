"""
图片文件解析器
支持多种图片格式的 OCR 文字识别
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
from PIL import Image
import cv2
import numpy as np

from ..base import BaseParser, ParseResult, FileType
from ..ocr.ocr_manager import OCRManager


class ImageParser(BaseParser):
    """图片文件解析器"""
    
    def __init__(self):
        super().__init__()
        self.ocr_manager = OCRManager()
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".gif"]
    
    @property
    def file_type(self) -> FileType:
        return FileType.IMAGE
    
    async def parse(self, file_path: Path) -> ParseResult:
        """
        解析图片文件
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            # 预处理图片
            processed_image = await self._preprocess_image(file_path)
            
            # 使用 OCR 提取文字
            ocr_text = await self._extract_text_with_ocr(processed_image)
            
            # 获取图片信息
            image_info = await self._get_image_info(file_path)
            
            metadata = self._get_file_metadata(file_path)
            metadata.update({
                "image_format": file_path.suffix.lower(),
                "image_info": image_info,
                "ocr_confidence": ocr_text.get("confidence", 0) if isinstance(ocr_text, dict) else 0
            })
            
            # 处理 OCR 结果
            if isinstance(ocr_text, dict):
                text_content = ocr_text.get("text", "")
                confidence = ocr_text.get("confidence", 0)
                method = ocr_text.get("method", "unknown")
                
                # 添加识别方法信息到元数据
                metadata["ocr_method"] = method
                metadata["ocr_confidence"] = confidence
            else:
                text_content = str(ocr_text)
            
            return ParseResult(
                filename=Path(file_path).name,
                file_type=self.file_type,
                text=text_content.strip(),
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"图片文件解析失败: {str(e)}")
            raise
    
    async def _preprocess_image(self, file_path: Path) -> Image.Image:
        """预处理图片以提高 OCR 效果"""
        def _preprocess():
            try:
                # 读取图片
                image = Image.open(file_path)
                
                # 转换为 RGB 模式
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # 转换为 OpenCV 格式进行预处理
                cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # 图片预处理
                processed = self._enhance_image_for_ocr(cv_image)
                
                # 转换回 PIL Image
                processed_image = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
                
                return processed_image
                
            except Exception as e:
                self.logger.warning(f"图片预处理失败: {str(e)}")
                # 如果预处理失败，返回原图
                return Image.open(file_path)
        
        return await asyncio.get_event_loop().run_in_executor(None, _preprocess)
    
    def _enhance_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """增强图片以提高 OCR 识别率，特别针对中文优化"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 检测图片质量并选择最佳处理策略
            quality_score = self._assess_image_quality(gray)
            self.logger.debug(f"图片质量评分: {quality_score}")
            
            if quality_score < 0.3:
                # 低质量图片：使用更激进的预处理
                processed = self._enhance_low_quality_image(gray)
            elif quality_score > 0.7:
                # 高质量图片：轻微处理
                processed = self._enhance_high_quality_image(gray)
            else:
                # 中等质量图片：标准处理
                processed = self._enhance_medium_quality_image(gray)
            
            # 文字方向检测和校正
            processed = self._correct_text_orientation(processed)
            
            return processed
            
        except Exception as e:
            self.logger.warning(f"图片增强失败: {str(e)}")
            return image
    
    def _assess_image_quality(self, gray_image: np.ndarray) -> float:
        """评估图片质量"""
        try:
            # 计算拉普拉斯方差（边缘清晰度）
            laplacian_var = cv2.Laplacian(gray_image, cv2.CV_64F).var()
            
            # 计算对比度
            contrast = gray_image.std()
            
            # 计算亮度分布
            hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
            brightness = np.argmax(hist) / 255.0
            
            # 综合评分 (0-1)
            quality_score = min(1.0, (laplacian_var / 1000 + contrast / 100 + (1 - abs(brightness - 0.5) * 2)) / 3)
            
            return quality_score
        except:
            return 0.5  # 默认中等质量
    
    def _enhance_low_quality_image(self, gray: np.ndarray) -> np.ndarray:
        """低质量图片增强"""
        # 高斯模糊去噪
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # 双边滤波保持边缘
        denoised = cv2.bilateralFilter(denoised, 9, 75, 75)
        
        # 自适应直方图均衡化
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 形态学操作去除噪点
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
        
        # 自适应阈值
        binary = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return binary
    
    def _enhance_medium_quality_image(self, gray: np.ndarray) -> np.ndarray:
        """中等质量图片增强"""
        # 中值滤波去噪
        denoised = cv2.medianBlur(gray, 3)
        
        # 对比度增强
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 锐化
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)
        
        # Otsu 二值化
        _, binary = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _enhance_high_quality_image(self, gray: np.ndarray) -> np.ndarray:
        """高质量图片轻微处理"""
        # 轻微降噪
        denoised = cv2.medianBlur(gray, 3)
        
        # 轻微对比度增强
        clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # 简单二值化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def _correct_text_orientation(self, image: np.ndarray) -> np.ndarray:
        """检测并校正文字方向"""
        try:
            # 使用 Tesseract 检测文字方向
            import pytesseract
            osd = pytesseract.image_to_osd(image, output_type=pytesseract.Output.DICT)
            
            # 获取旋转角度
            angle = osd.get('rotate', 0)
            confidence = osd.get('script_conf', 0)
            
            self.logger.debug(f"检测到文字方向角度: {angle}, 置信度: {confidence}")
            
            # 如果置信度足够高且角度不为0，则旋转图片
            if confidence > 5 and angle != 0:
                # 计算旋转中心
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                
                # 创建旋转矩阵
                rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
                
                # 执行旋转
                rotated = cv2.warpAffine(image, rotation_matrix, (w, h), 
                                       flags=cv2.INTER_CUBIC, 
                                       borderMode=cv2.BORDER_REPLICATE)
                
                return rotated
            
            return image
            
        except Exception as e:
            self.logger.debug(f"文字方向检测失败: {str(e)}")
            return image
    
    async def _extract_text_with_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """使用 OCR 提取文字，返回详细结果"""
        def _extract():
            try:
                # 使用多策略 OCR 识别
                return self._multi_strategy_ocr(image)
            except Exception as e:
                self.logger.error(f"OCR 文字提取失败: {str(e)}")
                return {
                    "text": f"[OCR 识别失败: {str(e)}]",
                    "confidence": 0,
                    "word_count": 0,
                    "char_count": 0,
                    "method": "error"
                }
        
        return await asyncio.get_event_loop().run_in_executor(None, _extract)
    
    def _multi_strategy_ocr(self, image: Image.Image) -> Dict[str, Any]:
        """多策略 OCR 识别"""
        # 使用 OCR 管理器的多引擎识别
        result = self.ocr_manager.extract_text_multi_engine(image)
        
        # 后处理：清理和优化结果
        result["text"] = self._post_process_ocr_text(result["text"])
        result["word_count"] = len(result["text"].split())
        result["char_count"] = len(result["text"])
        
        return result
    
    def _post_process_ocr_text(self, text: str) -> str:
        """OCR 结果后处理"""
        if not text:
            return ""
        
        import re
        
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 修复常见的中文 OCR 错误
        corrections = {
            r'[。，！？；：]': lambda m: m.group(0),  # 保留中文标点
            r'[a-zA-Z]': lambda m: m.group(0),  # 保留英文字母
            r'[0-9]': lambda m: m.group(0),  # 保留数字
            r'[\u4e00-\u9fff]': lambda m: m.group(0),  # 保留中文字符
        }
        
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        
        # 移除空行
        lines = [line for line in lines if line]
        
        # 重新组合
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text.strip()
    
    async def _get_image_info(self, file_path: Path) -> Dict[str, Any]:
        """获取图片信息"""
        def _get_info():
            try:
                with Image.open(file_path) as img:
                    return {
                        "width": img.width,
                        "height": img.height,
                        "mode": img.mode,
                        "format": img.format,
                        "size_bytes": file_path.stat().st_size
                    }
            except Exception as e:
                self.logger.warning(f"获取图片信息失败: {str(e)}")
                return {}
        
        return await asyncio.get_event_loop().run_in_executor(None, _get_info)

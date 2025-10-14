"""
OCR 管理器
自动选择最佳 OCR 引擎
"""

from typing import Dict, Any, List, Optional, Union
from PIL import Image
from loguru import logger

from .base_ocr import BaseOCR
from .tesseract_ocr import TesseractOCR
from ..config.ocr_config import OCRConfig


class OCRManager:
    """OCR 管理器，自动选择最佳引擎"""
    
    def __init__(self, config: OCRConfig = None):
        """
        初始化 OCR 管理器
        
        Args:
            config: OCR 配置
        """
        self.logger = logger.bind(ocr="OCRManager")
        self.config = config or OCRConfig.get_default_config()
        self.engines: Dict[str, BaseOCR] = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """初始化所有可用的 OCR 引擎"""
        # 初始化 TesseractOCR
        try:
            tesseract_ocr = TesseractOCR()
            self.engines["tesseract"] = tesseract_ocr
            self.logger.info("TesseractOCR 初始化成功")
        except Exception as e:
            self.logger.error(f"TesseractOCR 初始化失败: {str(e)}")
            self.logger.error("请确保已正确安装 TesseractOCR")
            raise
        
        self.logger.info("OCR 引擎初始化完成")
    
    def get_best_engine(self, image: Union[str, Image.Image] = None) -> Optional[BaseOCR]:
        """
        获取最佳 OCR 引擎
        
        Args:
            image: 图片路径字符串或PIL Image 对象（用于分析选择最佳引擎）
            
        Returns:
            BaseOCR: 最佳 OCR 引擎
        """
        if not self.engines:
            return None
        
        # 返回 TesseractOCR 引擎
        return self.engines.get("tesseract")
    
    def extract_text(self, image: Union[str, Image.Image], config: str = None) -> str:
        """
        从图片中提取文字
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: 配置参数
            
        Returns:
            str: 提取的文字
        """
        engine = self.get_best_engine(image)
        if engine is None:
            return "[没有可用的 OCR 引擎]"
        
        return engine.extract_text(image, config)
    
    def extract_text_with_confidence(self, image: Union[str, Image.Image], config: str = None) -> Dict[str, Any]:
        """
        从图片中提取文字并返回置信度信息
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: 配置参数
            
        Returns:
            Dict[str, Any]: 包含文字和置信度的字典
        """
        engine = self.get_best_engine(image)
        if engine is None:
            return {
                "text": "[没有可用的 OCR 引擎]",
                "confidence": 0,
                "word_count": 0,
                "char_count": 0,
                "method": "none"
            }
        
        result = engine.extract_text_with_confidence(image, config)
        result["engine"] = engine.__class__.__name__
        return result
    
    def extract_text_multi_engine(self, image: Union[str, Image.Image]) -> Dict[str, Any]:
        """
        使用 OCR 引擎提取文字
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            
        Returns:
            Dict[str, Any]: 识别结果
        """
        engine = self.get_best_engine(image)
        if engine is None:
            return {
                "text": "[没有可用的 OCR 引擎]",
                "confidence": 0,
                "word_count": 0,
                "char_count": 0,
                "method": "none"
            }
        
        try:
            result = engine.extract_text_with_confidence(image)
            result["engine"] = "tesseract"
            self.logger.debug(f"TesseractOCR 识别结果: 置信度 {result.get('confidence', 0):.1f}%, 长度 {len(result.get('text', ''))}")
            return result
        except Exception as e:
            self.logger.error(f"TesseractOCR 识别失败: {str(e)}")
            return {
                "text": f"[OCR 识别失败: {str(e)}]",
                "confidence": 0,
                "word_count": 0,
                "char_count": 0,
                "method": "tesseract_failed"
            }
    
    def get_available_languages(self) -> List[str]:
        """
        获取所有引擎支持的语言
        
        Returns:
            List[str]: 支持的语言列表
        """
        all_languages = set()
        for engine in self.engines.values():
            try:
                languages = engine.get_available_languages()
                all_languages.update(languages)
            except Exception as e:
                self.logger.warning(f"获取语言列表失败: {str(e)}")
        
        return list(all_languages)
    
    def set_language(self, lang: str):
        """
        设置所有引擎的语言
        
        Args:
            lang: 语言代码
        """
        for engine_name, engine in self.engines.items():
            try:
                engine.set_language(lang)
                self.logger.info(f"{engine_name} 语言设置为: {lang}")
            except Exception as e:
                self.logger.warning(f"{engine_name} 设置语言失败: {str(e)}")
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        获取引擎信息
        
        Returns:
            Dict[str, Any]: 引擎信息
        """
        info = {
            "available_engines": list(self.engines.keys()),
            "engines": {}
        }
        
        for engine_name, engine in self.engines.items():
            try:
                info["engines"][engine_name] = {
                    "class": engine.__class__.__name__,
                    "languages": engine.get_available_languages()
                }
            except Exception as e:
                info["engines"][engine_name] = {
                    "class": engine.__class__.__name__,
                    "error": str(e)
                }
        
        return info

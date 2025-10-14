"""
OCR 基础接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union
from PIL import Image


class BaseOCR(ABC):
    """OCR 引擎基础接口"""
    
    @abstractmethod
    def extract_text(self, image: Union[str, Image.Image], config: str = None) -> str:
        """
        从图片中提取文字
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: 配置参数
            
        Returns:
            str: 提取的文字
        """
        pass
    
    @abstractmethod
    def extract_text_with_confidence(self, image: Union[str, Image.Image], config: str = None) -> Dict[str, Any]:
        """
        从图片中提取文字并返回置信度信息
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: 配置参数
            
        Returns:
            Dict[str, Any]: 包含文字和置信度的字典
        """
        pass
    
    @abstractmethod
    def get_available_languages(self) -> List[str]:
        """
        获取可用的语言列表
        
        Returns:
            List[str]: 可用语言列表
        """
        pass
    
    @abstractmethod
    def set_language(self, lang: str):
        """
        设置 OCR 语言
        
        Args:
            lang: 语言代码
        """
        pass

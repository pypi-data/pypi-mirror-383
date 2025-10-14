"""
OCR 配置类
"""

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass
class OCRConfig:
    """OCR 配置类"""
    
    # 置信度阈值配置
    high_confidence_threshold: float = 70.0
    medium_confidence_threshold: float = 50.0
    low_confidence_threshold: float = 30.0
    
    # 文本质量阈值
    min_text_quality: float = 0.3
    min_text_length: int = 5
    
    # 图片预处理配置
    enable_image_enhancement: bool = True
    enable_text_orientation_correction: bool = True
    enable_quality_assessment: bool = True
    
    # 中文优化配置
    chinese_optimization: bool = True
    chinese_punctuation_handling: bool = True
    
    # 结果过滤配置
    filter_low_quality_results: bool = True
    merge_similar_results: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        pass
    
    def get_confidence_level(self, confidence: float) -> str:
        """获取置信度等级"""
        if confidence >= self.high_confidence_threshold:
            return "high"
        elif confidence >= self.medium_confidence_threshold:
            return "medium"
        elif confidence >= self.low_confidence_threshold:
            return "low"
        else:
            return "very_low"
    
    def should_accept_result(self, result: Dict[str, Any]) -> bool:
        """判断是否应该接受识别结果"""
        if not result:
            return False
        
        confidence = result.get("confidence", 0)
        text_quality = result.get("text_quality", 0)
        text_length = len(result.get("text", ""))
        
        # 基本过滤条件
        if text_length < self.min_text_length:
            return False
        
        if self.filter_low_quality_results:
            if confidence < self.low_confidence_threshold and text_quality < self.min_text_quality:
                return False
        
        return True
    
    def get_result_priority(self, result: Dict[str, Any]) -> float:
        """计算结果优先级"""
        if not result:
            return 0.0
        
        confidence = result.get("confidence", 0)
        text_quality = result.get("text_quality", 0)
        text_length = len(result.get("text", ""))
        
        # 优先级计算：置信度 50% + 文本质量 30% + 文本长度 20%
        priority = (
            confidence * 0.5 +
            text_quality * 100 * 0.3 +
            min(1.0, text_length / 100) * 100 * 0.2
        )
        
        return priority
    
    def get_engine_preference(self) -> List[str]:
        """获取引擎优先级列表"""
        return ["tesseract"]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "high_confidence_threshold": self.high_confidence_threshold,
            "medium_confidence_threshold": self.medium_confidence_threshold,
            "low_confidence_threshold": self.low_confidence_threshold,
            "min_text_quality": self.min_text_quality,
            "min_text_length": self.min_text_length,
            "enable_image_enhancement": self.enable_image_enhancement,
            "enable_text_orientation_correction": self.enable_text_orientation_correction,
            "enable_quality_assessment": self.enable_quality_assessment,
            "chinese_optimization": self.chinese_optimization,
            "chinese_punctuation_handling": self.chinese_punctuation_handling,
            "filter_low_quality_results": self.filter_low_quality_results,
            "merge_similar_results": self.merge_similar_results
        }
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'OCRConfig':
        """从字典创建配置"""
        return cls(**config_dict)
    
    @classmethod
    def get_default_config(cls) -> 'OCRConfig':
        """获取默认配置"""
        return cls()
    
    @classmethod
    def get_chinese_optimized_config(cls) -> 'OCRConfig':
        """获取中文优化配置"""
        return cls(
            high_confidence_threshold=75.0,
            medium_confidence_threshold=55.0,
            low_confidence_threshold=35.0,
            min_text_quality=0.4,
            min_text_length=3,
            chinese_optimization=True,
            chinese_punctuation_handling=True
        )
    
    @classmethod
    def get_high_accuracy_config(cls) -> 'OCRConfig':
        """获取高精度配置"""
        return cls(
            high_confidence_threshold=80.0,
            medium_confidence_threshold=60.0,
            low_confidence_threshold=40.0,
            min_text_quality=0.5,
            min_text_length=10,
            filter_low_quality_results=True,
            merge_similar_results=True
        )
    
    @classmethod
    def get_fast_config(cls) -> 'OCRConfig':
        """获取快速配置"""
        return cls(
            high_confidence_threshold=60.0,
            medium_confidence_threshold=40.0,
            low_confidence_threshold=20.0,
            min_text_quality=0.2,
            min_text_length=2,
            enable_image_enhancement=False,
            filter_low_quality_results=False
        )
    
    @classmethod
    def get_tesseract_optimized_config(cls) -> 'OCRConfig':
        """获取TesseractOCR优化配置"""
        return cls(
            high_confidence_threshold=75.0,
            medium_confidence_threshold=55.0,
            low_confidence_threshold=35.0,
            min_text_quality=0.4,
            min_text_length=3,
            chinese_optimization=True,
            chinese_punctuation_handling=True
        )

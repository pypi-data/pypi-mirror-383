"""
基础解析器类和数据结构定义
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import asyncio
from loguru import logger


class FileType(Enum):
    """支持的文件类型枚举"""
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    POWERPOINT = "powerpoint"
    IMAGE = "image"
    TEXT = "text"
    CSV = "csv"
    UNKNOWN = "unknown"


@dataclass
class ParseResult:
    """解析结果数据结构"""
    filename: str
    file_type: FileType
    text: str
    metadata: Dict[str, Any]
    success: bool
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    
    def __post_init__(self):
        """后处理，确保文本不为空"""
        if self.text is None:
            self.text = ""


class BaseParser(ABC):
    """文件解析器基类"""
    
    def __init__(self):
        self.logger = logger.bind(parser=self.__class__.__name__)
    
    @property
    @abstractmethod
    def supported_extensions(self) -> List[str]:
        """返回支持的文件扩展名列表"""
        pass
    
    @property
    @abstractmethod
    def file_type(self) -> FileType:
        """返回文件类型"""
        pass
    
    @abstractmethod
    async def parse(self, file_path: Union[str, Path]) -> ParseResult:
        """
        解析文件并返回结果
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        pass
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        检查是否可以解析指定文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否可以解析
        """
        path = Path(file_path)
        return path.suffix.lower() in self.supported_extensions
    
    def _get_file_metadata(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        获取文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 文件元数据
        """
        path = Path(file_path)
        return {
            "filename": path.name,
            "file_size": path.stat().st_size if path.exists() else 0,
            "file_extension": path.suffix.lower(),
            "file_type": self.file_type.value
        }
    
    async def _safe_parse(self, file_path: Union[str, Path]) -> ParseResult:
        """
        安全的解析方法，包含错误处理
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        import time
        start_time = time.time()
        
        try:
            self.logger.info(f"开始解析文件: {file_path}")
            
            # 检查文件是否存在
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
            
            # 执行解析
            result = await self.parse(file_path)
            result.processing_time = time.time() - start_time
            
            self.logger.info(f"文件解析完成: {file_path}, 耗时: {result.processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"解析文件失败: {str(e)}"
            self.logger.error(f"{error_msg}, 文件: {file_path}")
            
            return ParseResult(
                filename=Path(file_path).name,
                file_type=self.file_type,
                text="",
                metadata=self._get_file_metadata(file_path),
                success=False,
                error_message=error_msg,
                processing_time=processing_time
            )

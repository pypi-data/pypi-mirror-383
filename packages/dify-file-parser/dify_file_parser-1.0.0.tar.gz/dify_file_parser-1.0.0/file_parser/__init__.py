"""
文件解析器 - 支持多种文件格式转换为 AI 可识别的文本

基于 Dify 项目文件处理功能抽离的通用文件解析器
"""

from .base import BaseParser, ParseResult, FileType
from .file_parser import FileParser

__version__ = "1.0.0"
__author__ = "File Parser Team"

__all__ = [
    "BaseParser",
    "ParseResult",
    "FileType",
    "FileParser"
]

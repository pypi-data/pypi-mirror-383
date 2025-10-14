"""
主文件解析器类
提供统一的文件解析接口
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from loguru import logger

from .base import BaseParser, ParseResult, FileType
from .parsers import (
    PDFParser, WordParser, ExcelParser, PPTParser,
    ImageParser, TextParser, CSVParser
)
from .utils.file_utils import FileUtils


class FileParser:
    """主文件解析器类"""
    
    def __init__(self, max_concurrent: int = 5):
        """
        初始化文件解析器
        
        Args:
            max_concurrent: 最大并发处理数
        """
        self.logger = logger.bind(component="FileParser")
        self.max_concurrent = max_concurrent
        
        # 初始化所有解析器
        self.parsers: Dict[FileType, BaseParser] = {
            FileType.PDF: PDFParser(),
            FileType.WORD: WordParser(),
            FileType.EXCEL: ExcelParser(),
            FileType.POWERPOINT: PPTParser(),
            FileType.IMAGE: ImageParser(),
            FileType.TEXT: TextParser(),
            FileType.CSV: CSVParser(),
        }
        
        # 创建扩展名到文件类型的映射
        self.extension_to_type: Dict[str, FileType] = {}
        for parser in self.parsers.values():
            for ext in parser.supported_extensions:
                self.extension_to_type[ext] = parser.file_type
        
        self.logger.info(f"文件解析器初始化完成，支持 {len(self.parsers)} 种文件类型")
    
    def get_supported_extensions(self) -> List[str]:
        """
        获取所有支持的文件扩展名
        
        Returns:
            List[str]: 支持的扩展名列表
        """
        return list(self.extension_to_type.keys())
    
    def get_supported_types(self) -> List[FileType]:
        """
        获取所有支持的文件类型
        
        Returns:
            List[FileType]: 支持的文件类型列表
        """
        return list(self.parsers.keys())
    
    def can_parse(self, file_path: Union[str, Path]) -> bool:
        """
        检查是否可以解析指定文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 是否可以解析
        """
        extension = FileUtils.get_file_extension(str(file_path))
        return extension in self.extension_to_type
    
    def get_file_type(self, file_path: Union[str, Path]) -> FileType:
        """
        获取文件类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            FileType: 文件类型
        """
        extension = FileUtils.get_file_extension(str(file_path))
        return self.extension_to_type.get(extension, FileType.UNKNOWN)
    
    async def parse_file(self, file_path: Union[str, Path]) -> ParseResult:
        """
        解析单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        file_path = Path(file_path)
        
        # 检查文件是否存在
        if not file_path.exists():
            return ParseResult(
                filename=file_path.name,
                file_type=FileType.UNKNOWN,
                text="",
                metadata={"error": "文件不存在"},
                success=False,
                error_message=f"文件不存在: {file_path}"
            )
        
        # 检查是否支持该文件类型
        if not self.can_parse(file_path):
            return ParseResult(
                filename=file_path.name,
                file_type=FileType.UNKNOWN,
                text="",
                metadata={"error": "不支持的文件类型"},
                success=False,
                error_message=f"不支持的文件类型: {file_path.suffix}"
            )
        
        # 获取对应的解析器
        file_type = self.get_file_type(file_path)
        parser = self.parsers[file_type]
        
        self.logger.info(f"开始解析文件: {file_path} (类型: {file_type.value})")
        
        # 执行解析
        result = await parser._safe_parse(file_path)
        
        self.logger.info(f"文件解析完成: {file_path}, 成功: {result.success}")
        return result
    
    async def parse_files(self, file_paths: List[Union[str, Path]], 
                         max_concurrent: Optional[int] = None) -> List[ParseResult]:
        """
        批量解析文件
        
        Args:
            file_paths: 文件路径列表
            max_concurrent: 最大并发数，None 使用默认值
            
        Returns:
            List[ParseResult]: 解析结果列表
        """
        if max_concurrent is None:
            max_concurrent = self.max_concurrent
        
        self.logger.info(f"开始批量解析 {len(file_paths)} 个文件，最大并发: {max_concurrent}")
        
        # 创建信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def parse_with_semaphore(file_path):
            async with semaphore:
                return await self.parse_file(file_path)
        
        # 并发执行解析任务
        tasks = [parse_with_semaphore(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(ParseResult(
                    filename=Path(file_paths[i]).name,
                    file_type=FileType.UNKNOWN,
                    text="",
                    metadata={"error": str(result)},
                    success=False,
                    error_message=f"解析异常: {str(result)}"
                ))
            else:
                processed_results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in processed_results if r.success)
        self.logger.info(f"批量解析完成: 成功 {success_count}/{len(file_paths)}")
        
        return processed_results
    
    async def parse_directory(self, directory_path: Union[str, Path], 
                            recursive: bool = True,
                            file_patterns: Optional[List[str]] = None) -> List[ParseResult]:
        """
        解析目录中的所有文件
        
        Args:
            directory_path: 目录路径
            recursive: 是否递归搜索子目录
            file_patterns: 文件模式列表，如 ['*.pdf', '*.docx']
            
        Returns:
            List[ParseResult]: 解析结果列表
        """
        directory_path = Path(directory_path)
        
        if not directory_path.exists() or not directory_path.is_dir():
            self.logger.error(f"目录不存在或不是目录: {directory_path}")
            return []
        
        # 收集文件
        file_paths = []
        if file_patterns:
            for pattern in file_patterns:
                if recursive:
                    file_paths.extend(directory_path.rglob(pattern))
                else:
                    file_paths.extend(directory_path.glob(pattern))
        else:
            # 只收集支持的文件类型
            supported_extensions = self.get_supported_extensions()
            for ext in supported_extensions:
                if recursive:
                    file_paths.extend(directory_path.rglob(f"*{ext}"))
                else:
                    file_paths.extend(directory_path.glob(f"*{ext}"))
        
        # 过滤出实际存在的文件
        file_paths = [f for f in file_paths if f.is_file()]
        
        self.logger.info(f"在目录 {directory_path} 中找到 {len(file_paths)} 个文件")
        
        if not file_paths:
            return []
        
        # 批量解析
        return await self.parse_files(file_paths)
    
    def get_parser_info(self) -> Dict[str, Any]:
        """
        获取解析器信息
        
        Returns:
            Dict[str, Any]: 解析器信息
        """
        info = {
            "supported_types": [t.value for t in self.get_supported_types()],
            "supported_extensions": self.get_supported_extensions(),
            "parsers": {}
        }
        
        for file_type, parser in self.parsers.items():
            info["parsers"][file_type.value] = {
                "class": parser.__class__.__name__,
                "extensions": parser.supported_extensions,
                "description": parser.__doc__ or "无描述"
            }
        
        return info

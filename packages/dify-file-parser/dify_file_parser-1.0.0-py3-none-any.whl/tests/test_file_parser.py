"""
文件解析器测试
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

from file_parser import FileParser, FileType, ParseResult


class TestFileParser:
    """文件解析器测试类"""
    
    @pytest.fixture
    def parser(self):
        """创建解析器实例"""
        return FileParser()
    
    def test_initialization(self, parser):
        """测试初始化"""
        assert parser.max_concurrent == 5
        assert len(parser.parsers) == 7  # 7种文件类型
        assert len(parser.extension_to_type) > 0
    
    def test_get_supported_extensions(self, parser):
        """测试获取支持的扩展名"""
        extensions = parser.get_supported_extensions()
        assert isinstance(extensions, list)
        assert ".pdf" in extensions
        assert ".docx" in extensions
        assert ".txt" in extensions
    
    def test_get_supported_types(self, parser):
        """测试获取支持的类型"""
        types = parser.get_supported_types()
        assert isinstance(types, list)
        assert FileType.PDF in types
        assert FileType.WORD in types
        assert FileType.TEXT in types
    
    def test_can_parse(self, parser):
        """测试文件解析能力检查"""
        assert parser.can_parse("test.pdf")
        assert parser.can_parse("test.docx")
        assert parser.can_parse("test.txt")
        assert not parser.can_parse("test.unknown")
    
    def test_get_file_type(self, parser):
        """测试获取文件类型"""
        assert parser.get_file_type("test.pdf") == FileType.PDF
        assert parser.get_file_type("test.docx") == FileType.WORD
        assert parser.get_file_type("test.txt") == FileType.TEXT
        assert parser.get_file_type("test.unknown") == FileType.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_parse_nonexistent_file(self, parser):
        """测试解析不存在的文件"""
        result = await parser.parse_file("nonexistent.pdf")
        assert not result.success
        assert "文件不存在" in result.error_message
        assert result.file_type == FileType.UNKNOWN
    
    @pytest.mark.asyncio
    async def test_parse_unsupported_file(self, parser):
        """测试解析不支持的文件"""
        # 创建一个不支持的临时文件
        temp_file = Path("test.unknown")
        temp_file.write_text("test content")
        
        try:
            result = await parser.parse_file(temp_file)
            assert not result.success
            assert "不支持的文件类型" in result.error_message
        finally:
            temp_file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_parse_text_file(self, parser):
        """测试解析文本文件"""
        # 创建测试文本文件
        test_content = "这是一个测试文件\n包含多行文本\n用于测试解析功能"
        temp_file = Path("test.txt")
        temp_file.write_text(test_content, encoding="utf-8")
        
        try:
            result = await parser.parse_file(temp_file)
            assert result.success
            assert result.file_type == FileType.TEXT
            assert "测试文件" in result.text
            assert result.processing_time is not None
        finally:
            temp_file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_parse_files_batch(self, parser):
        """测试批量解析文件"""
        # 创建多个测试文件
        test_files = []
        for i in range(3):
            temp_file = Path(f"test_{i}.txt")
            temp_file.write_text(f"测试文件 {i}", encoding="utf-8")
            test_files.append(temp_file)
        
        try:
            results = await parser.parse_files(test_files)
            assert len(results) == 3
            assert all(r.success for r in results)
            assert all(r.file_type == FileType.TEXT for r in results)
        finally:
            for temp_file in test_files:
                temp_file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_parse_directory(self, parser):
        """测试解析目录"""
        # 创建测试目录和文件
        test_dir = Path("test_dir")
        test_dir.mkdir(exist_ok=True)
        
        test_files = []
        for i in range(3):
            temp_file = test_dir / f"test_{i}.txt"
            temp_file.write_text(f"测试文件 {i}", encoding="utf-8")
            test_files.append(temp_file)
        
        try:
            results = await parser.parse_directory(test_dir)
            assert len(results) == 3
            assert all(r.success for r in results)
        finally:
            for temp_file in test_files:
                temp_file.unlink(missing_ok=True)
            test_dir.rmdir()
    
    def test_get_parser_info(self, parser):
        """测试获取解析器信息"""
        info = parser.get_parser_info()
        assert "supported_types" in info
        assert "supported_extensions" in info
        assert "parsers" in info
        assert len(info["supported_types"]) > 0
        assert len(info["supported_extensions"]) > 0


class TestParseResult:
    """解析结果测试类"""
    
    def test_parse_result_creation(self):
        """测试解析结果创建"""
        result = ParseResult(
            filename="test.txt",
            file_type=FileType.TEXT,
            text="测试内容",
            metadata={"test": "value"},
            success=True
        )
        
        assert result.filename == "test.txt"
        assert result.file_type == FileType.TEXT
        assert result.text == "测试内容"
        assert result.metadata == {"test": "value"}
        assert result.success is True
        assert result.error_message is None
    
    def test_parse_result_post_init(self):
        """测试解析结果后处理"""
        result = ParseResult(
            filename="test.txt",
            file_type=FileType.TEXT,
            text=None,  # 测试 None 值处理
            metadata={},
            success=True
        )
        
        assert result.text == ""  # 应该被设置为空字符串


@pytest.mark.asyncio
async def test_concurrent_parsing():
    """测试并发解析"""
    parser = FileParser(max_concurrent=2)
    
    # 创建多个测试文件
    test_files = []
    for i in range(5):
        temp_file = Path(f"concurrent_test_{i}.txt")
        temp_file.write_text(f"并发测试文件 {i}", encoding="utf-8")
        test_files.append(temp_file)
    
    try:
        results = await parser.parse_files(test_files)
        assert len(results) == 5
        assert all(r.success for r in results)
    finally:
        for temp_file in test_files:
            temp_file.unlink(missing_ok=True)

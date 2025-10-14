"""
解析器测试
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch

from file_parser.parsers import (
    PDFParser, WordParser, ExcelParser, PPTParser,
    ImageParser, TextParser, CSVParser
)
from file_parser.base import FileType


class TestTextParser:
    """文本解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return TextParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".txt" in parser.supported_extensions
        assert ".md" in parser.supported_extensions
        assert ".log" in parser.supported_extensions
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.TEXT
    
    def test_can_parse(self, parser):
        """测试解析能力"""
        assert parser.can_parse("test.txt")
        assert parser.can_parse("test.md")
        assert not parser.can_parse("test.pdf")
    
    @pytest.mark.asyncio
    async def test_parse_text_file(self, parser):
        """测试解析文本文件"""
        # 创建测试文件
        test_content = "这是一个测试文件\n包含多行文本\n用于测试解析功能"
        temp_file = Path("test_parser.txt")
        temp_file.write_text(test_content, encoding="utf-8")
        
        try:
            result = await parser._safe_parse(temp_file)
            assert result.success
            assert "测试文件" in result.text
            assert result.file_type == FileType.TEXT
            assert result.processing_time is not None
        finally:
            temp_file.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_parse_markdown_file(self, parser):
        """测试解析 Markdown 文件"""
        # 创建测试 Markdown 文件
        test_content = """# 测试标题
        
这是一个 **粗体** 文本。

- 列表项 1
- 列表项 2

## 子标题

普通文本内容。
"""
        temp_file = Path("test_parser.md")
        temp_file.write_text(test_content, encoding="utf-8")
        
        try:
            result = await parser._safe_parse(temp_file)
            assert result.success
            assert "测试标题" in result.text
            assert "粗体" in result.text
            assert result.file_type == FileType.TEXT
        finally:
            temp_file.unlink(missing_ok=True)


class TestCSVParser:
    """CSV 解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return CSVParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".csv" in parser.supported_extensions
        assert len(parser.supported_extensions) == 1
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.CSV
    
    @pytest.mark.asyncio
    async def test_parse_csv_file(self, parser):
        """测试解析 CSV 文件"""
        # 创建测试 CSV 文件
        test_content = """姓名,年龄,城市
张三,25,北京
李四,30,上海
王五,28,广州
"""
        temp_file = Path("test_parser.csv")
        temp_file.write_text(test_content, encoding="utf-8")
        
        try:
            result = await parser._safe_parse(temp_file)
            assert result.success
            assert "姓名" in result.text
            assert "张三" in result.text
            assert result.file_type == FileType.CSV
        finally:
            temp_file.unlink(missing_ok=True)


class TestImageParser:
    """图片解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return ImageParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".jpg" in parser.supported_extensions
        assert ".png" in parser.supported_extensions
        assert ".bmp" in parser.supported_extensions
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.IMAGE
    
    @pytest.mark.asyncio
    async def test_parse_nonexistent_image(self, parser):
        """测试解析不存在的图片文件"""
        result = await parser._safe_parse("nonexistent.png")
        assert not result.success
        assert "文件不存在" in result.error_message


class TestPDFParser:
    """PDF 解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return PDFParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".pdf" in parser.supported_extensions
        assert len(parser.supported_extensions) == 1
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.PDF
    
    @pytest.mark.asyncio
    async def test_parse_nonexistent_pdf(self, parser):
        """测试解析不存在的 PDF 文件"""
        result = await parser._safe_parse("nonexistent.pdf")
        assert not result.success
        assert "文件不存在" in result.error_message


class TestWordParser:
    """Word 解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return WordParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".docx" in parser.supported_extensions
        assert ".doc" in parser.supported_extensions
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.WORD


class TestExcelParser:
    """Excel 解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return ExcelParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".xlsx" in parser.supported_extensions
        assert ".xls" in parser.supported_extensions
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.EXCEL


class TestPPTParser:
    """PowerPoint 解析器测试"""
    
    @pytest.fixture
    def parser(self):
        return PPTParser()
    
    def test_supported_extensions(self, parser):
        """测试支持的扩展名"""
        assert ".pptx" in parser.supported_extensions
        assert ".ppt" in parser.supported_extensions
    
    def test_file_type(self, parser):
        """测试文件类型"""
        assert parser.file_type == FileType.POWERPOINT

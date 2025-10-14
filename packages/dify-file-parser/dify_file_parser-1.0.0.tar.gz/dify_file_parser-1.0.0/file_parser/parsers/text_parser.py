"""
文本文件解析器
支持 .txt, .md 等纯文本格式
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import chardet
import markdown

from ..base import BaseParser, ParseResult, FileType


class TextParser(BaseParser):
    """文本文件解析器"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".txt", ".md", ".markdown", ".rst", ".log"]
    
    @property
    def file_type(self) -> FileType:
        return FileType.TEXT
    
    async def parse(self, file_path: Path) -> ParseResult:
        """
        解析文本文件
        
        Args:
            file_path: 文本文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            # 检测文件编码
            encoding = await self._detect_encoding(file_path)
            
            # 读取文件内容
            text_content = await self._read_file_content(file_path, encoding)
            
            # 如果是 Markdown 文件，转换为纯文本
            if file_path.suffix.lower() in [".md", ".markdown"]:
                text_content = await self._convert_markdown_to_text(text_content)
            
            # 获取文件统计信息
            stats = self._get_text_stats(text_content)
            
            metadata = self._get_file_metadata(file_path)
            metadata.update({
                "text_format": file_path.suffix.lower(),
                "encoding": encoding,
                "stats": stats
            })
            
            return ParseResult(
                filename=Path(file_path).name,
                file_type=self.file_type,
                text=text_content.strip(),
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"文本文件解析失败: {str(e)}")
            raise
    
    async def _detect_encoding(self, file_path: Path) -> str:
        """检测文件编码"""
        def _detect():
            try:
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)  # 读取前10KB用于检测
                    result = chardet.detect(raw_data)
                    encoding = result.get('encoding', 'utf-8')
                    confidence = result.get('confidence', 0)
                    
                    self.logger.info(f"检测到编码: {encoding}, 置信度: {confidence:.2f}")
                    return encoding
            except Exception as e:
                self.logger.warning(f"编码检测失败: {str(e)}, 使用默认编码 utf-8")
                return 'utf-8'
        
        return await asyncio.get_event_loop().run_in_executor(None, _detect)
    
    async def _read_file_content(self, file_path: Path, encoding: str) -> str:
        """读取文件内容"""
        def _read():
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                # 如果指定编码失败，尝试其他常见编码
                for fallback_encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
                    try:
                        with open(file_path, 'r', encoding=fallback_encoding) as f:
                            self.logger.info(f"使用备用编码 {fallback_encoding} 成功读取文件")
                            return f.read()
                    except UnicodeDecodeError:
                        continue
                
                # 如果所有编码都失败，使用错误处理模式
                with open(file_path, 'r', encoding=encoding, errors='replace') as f:
                    self.logger.warning(f"使用错误处理模式读取文件，可能有乱码")
                    return f.read()
        
        return await asyncio.get_event_loop().run_in_executor(None, _read)
    
    async def _convert_markdown_to_text(self, markdown_content: str) -> str:
        """将 Markdown 转换为纯文本"""
        def _convert():
            try:
                # 使用 markdown 库转换为 HTML
                html = markdown.markdown(markdown_content)
                
                # 简单的 HTML 标签清理
                import re
                # 移除 HTML 标签
                text = re.sub(r'<[^>]+>', '', html)
                # 解码 HTML 实体
                import html
                text = html.unescape(text)
                
                return text
            except Exception as e:
                self.logger.warning(f"Markdown 转换失败: {str(e)}")
                return markdown_content
        
        return await asyncio.get_event_loop().run_in_executor(None, _convert)
    
    def _get_text_stats(self, text_content: str) -> Dict[str, Any]:
        """获取文本统计信息"""
        try:
            lines = text_content.split('\n')
            words = text_content.split()
            
            return {
                "char_count": len(text_content),
                "line_count": len(lines),
                "word_count": len(words),
                "non_empty_line_count": len([line for line in lines if line.strip()]),
                "avg_line_length": sum(len(line) for line in lines) / len(lines) if lines else 0
            }
        except Exception as e:
            self.logger.warning(f"获取文本统计信息失败: {str(e)}")
            return {}

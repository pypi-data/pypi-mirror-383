"""
CSV 文件解析器
支持 .csv 格式的表格数据解析
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import csv

from ..base import BaseParser, ParseResult, FileType


class CSVParser(BaseParser):
    """CSV 文件解析器"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".csv"]
    
    @property
    def file_type(self) -> FileType:
        return FileType.CSV
    
    async def parse(self, file_path: Path) -> ParseResult:
        """
        解析 CSV 文件
        
        Args:
            file_path: CSV 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            # 检测 CSV 格式
            csv_info = await self._detect_csv_format(file_path)
            
            # 解析 CSV 内容
            text_content = await self._parse_csv_content(file_path, csv_info)
            
            # 获取 CSV 统计信息
            stats = await self._get_csv_stats(file_path, csv_info)
            
            metadata = self._get_file_metadata(file_path)
            metadata.update({
                "csv_format": file_path.suffix.lower(),
                "csv_info": csv_info,
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
            self.logger.error(f"CSV 文件解析失败: {str(e)}")
            raise
    
    async def _detect_csv_format(self, file_path: Path) -> Dict[str, Any]:
        """检测 CSV 文件格式"""
        def _detect():
            try:
                # 读取文件前几行来检测格式
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    sample = f.read(1024)
                
                # 检测分隔符
                sniffer = csv.Sniffer()
                try:
                    dialect = sniffer.sniff(sample)
                    delimiter = dialect.delimiter
                    quotechar = dialect.quotechar
                except:
                    # 如果检测失败，使用默认值
                    delimiter = ','
                    quotechar = '"'
                
                # 检测编码
                with open(file_path, 'rb') as f:
                    raw_data = f.read(10000)
                    import chardet
                    result = chardet.detect(raw_data)
                    encoding = result.get('encoding', 'utf-8')
                
                return {
                    "delimiter": delimiter,
                    "quotechar": quotechar,
                    "encoding": encoding
                }
                
            except Exception as e:
                self.logger.warning(f"CSV 格式检测失败: {str(e)}")
                return {
                    "delimiter": ",",
                    "quotechar": '"',
                    "encoding": "utf-8"
                }
        
        return await asyncio.get_event_loop().run_in_executor(None, _detect)
    
    async def _parse_csv_content(self, file_path: Path, csv_info: Dict[str, Any]) -> str:
        """解析 CSV 内容"""
        def _parse():
            try:
                # 使用 pandas 读取 CSV
                df = pd.read_csv(
                    file_path,
                    delimiter=csv_info["delimiter"],
                    quotechar=csv_info["quotechar"],
                    encoding=csv_info["encoding"],
                    on_bad_lines='skip'  # 跳过有问题的行
                )
                
                text_parts = []
                
                # 添加列名
                if not df.columns.empty:
                    header = " | ".join([str(col) for col in df.columns])
                    text_parts.append(f"列名: {header}")
                    text_parts.append("=" * len(header))
                
                # 添加数据行（限制行数避免过长）
                max_rows = 1000
                for idx, row in df.head(max_rows).iterrows():
                    row_text = " | ".join([str(cell) if pd.notna(cell) else "" for cell in row])
                    if row_text.strip():
                        text_parts.append(f"第{idx+1}行: {row_text}")
                
                if len(df) > max_rows:
                    text_parts.append(f"... (还有 {len(df) - max_rows} 行数据)")
                
                return "\n".join(text_parts)
                
            except Exception as e:
                self.logger.error(f"解析 CSV 内容失败: {str(e)}")
                # 如果 pandas 失败，尝试使用 csv 模块
                return self._parse_csv_with_builtin(file_path, csv_info)
        
        return await asyncio.get_event_loop().run_in_executor(None, _parse)
    
    def _parse_csv_with_builtin(self, file_path: Path, csv_info: Dict[str, Any]) -> str:
        """使用内置 csv 模块解析"""
        try:
            text_parts = []
            
            with open(file_path, 'r', encoding=csv_info["encoding"], errors='ignore') as f:
                reader = csv.reader(f, delimiter=csv_info["delimiter"], quotechar=csv_info["quotechar"])
                
                for row_num, row in enumerate(reader):
                    if row_num >= 1000:  # 限制行数
                        text_parts.append(f"... (还有更多行数据)")
                        break
                    
                    row_text = " | ".join([str(cell) for cell in row])
                    if row_text.strip():
                        text_parts.append(f"第{row_num+1}行: {row_text}")
            
            return "\n".join(text_parts)
            
        except Exception as e:
            self.logger.error(f"使用内置 csv 模块解析失败: {str(e)}")
            return f"[错误] CSV 文件解析失败: {str(e)}"
    
    async def _get_csv_stats(self, file_path: Path, csv_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取 CSV 统计信息"""
        def _get_stats():
            try:
                df = pd.read_csv(
                    file_path,
                    delimiter=csv_info["delimiter"],
                    quotechar=csv_info["quotechar"],
                    encoding=csv_info["encoding"],
                    on_bad_lines='skip'
                )
                
                return {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "column_names": list(df.columns),
                    "has_header": True,
                    "empty_rows": df.isnull().all(axis=1).sum()
                }
                
            except Exception as e:
                self.logger.warning(f"获取 CSV 统计信息失败: {str(e)}")
                return {}
        
        return await asyncio.get_event_loop().run_in_executor(None, _get_stats)

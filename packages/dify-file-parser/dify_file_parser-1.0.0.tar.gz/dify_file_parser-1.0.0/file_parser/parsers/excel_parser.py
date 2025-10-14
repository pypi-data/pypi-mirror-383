"""
Excel 文件解析器
支持 .xlsx 和 .xls 格式
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Any
import openpyxl
import pandas as pd

from ..base import BaseParser, ParseResult, FileType


class ExcelParser(BaseParser):
    """Excel 文件解析器"""
    
    @property
    def supported_extensions(self) -> List[str]:
        return [".xlsx", ".xls"]
    
    @property
    def file_type(self) -> FileType:
        return FileType.EXCEL
    
    async def parse(self, file_path: Path) -> ParseResult:
        """
        解析 Excel 文件
        
        Args:
            file_path: Excel 文件路径
            
        Returns:
            ParseResult: 解析结果
        """
        try:
            text_content = await self._extract_excel_content(file_path)
            
            # 获取工作表信息
            sheet_info = await self._get_sheet_info(file_path)
            
            metadata = self._get_file_metadata(file_path)
            metadata.update({
                "excel_format": file_path.suffix.lower(),
                "sheet_count": len(sheet_info),
                "sheets": sheet_info
            })
            
            return ParseResult(
                filename=Path(file_path).name,
                file_type=self.file_type,
                text=text_content.strip(),
                metadata=metadata,
                success=True
            )
            
        except Exception as e:
            self.logger.error(f"Excel 文件解析失败: {str(e)}")
            raise
    
    async def _extract_excel_content(self, file_path: Path) -> str:
        """提取 Excel 内容"""
        def _extract():
            try:
                # 使用 pandas 读取所有工作表
                excel_file = pd.ExcelFile(file_path)
                text_parts = []
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        
                        # 跳过空工作表
                        if df.empty:
                            continue
                        
                        # 添加工作表标题
                        text_parts.append(f"=== 工作表: {sheet_name} ===")
                        
                        # 处理数据
                        if len(df) > 0:
                            # 如果有列名，添加表头
                            if not df.columns.empty:
                                header = " | ".join([str(col) for col in df.columns])
                                text_parts.append(f"列名: {header}")
                            
                            # 添加数据行（限制行数避免过长）
                            max_rows = 100
                            for idx, row in df.head(max_rows).iterrows():
                                row_text = " | ".join([str(cell) if pd.notna(cell) else "" for cell in row])
                                if row_text.strip():
                                    text_parts.append(f"第{idx+1}行: {row_text}")
                            
                            if len(df) > max_rows:
                                text_parts.append(f"... (还有 {len(df) - max_rows} 行数据)")
                        
                        text_parts.append("")  # 空行分隔
                        
                    except Exception as e:
                        self.logger.warning(f"处理工作表 {sheet_name} 失败: {str(e)}")
                        text_parts.append(f"[错误] 无法处理工作表 {sheet_name}: {str(e)}")
                
                return "\n".join(text_parts)
                
            except Exception as e:
                self.logger.error(f"提取 Excel 内容失败: {str(e)}")
                raise
        
        return await asyncio.get_event_loop().run_in_executor(None, _extract)
    
    async def _get_sheet_info(self, file_path: Path) -> List[Dict[str, Any]]:
        """获取工作表信息"""
        def _get_info():
            try:
                excel_file = pd.ExcelFile(file_path)
                sheet_info = []
                
                for sheet_name in excel_file.sheet_names:
                    try:
                        df = pd.read_excel(file_path, sheet_name=sheet_name)
                        sheet_info.append({
                            "name": sheet_name,
                            "rows": len(df),
                            "columns": len(df.columns),
                            "column_names": list(df.columns) if not df.columns.empty else []
                        })
                    except Exception as e:
                        sheet_info.append({
                            "name": sheet_name,
                            "rows": 0,
                            "columns": 0,
                            "column_names": [],
                            "error": str(e)
                        })
                
                return sheet_info
                
            except Exception as e:
                self.logger.error(f"获取工作表信息失败: {str(e)}")
                return []
        
        return await asyncio.get_event_loop().run_in_executor(None, _get_info)

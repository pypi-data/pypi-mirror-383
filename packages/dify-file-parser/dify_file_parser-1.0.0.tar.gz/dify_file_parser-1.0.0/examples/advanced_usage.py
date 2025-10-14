"""
高级使用示例
"""

import asyncio
from pathlib import Path
from file_parser import FileParser, FileType


async def main():
    """高级使用示例"""
    # 创建解析器实例，设置最大并发数
    parser = FileParser(max_concurrent=3)
    
    # 解析整个目录
    sample_dir = Path("sample")
    if sample_dir.exists():
        print(f"解析目录: {sample_dir}")
        results = await parser.parse_directory(
            sample_dir,
            recursive=True,
            file_patterns=["*.pdf", "*.docx", "*.txt"]  # 只解析特定格式
        )
        
        print(f"目录解析完成: 找到 {len(results)} 个文件")
        
        # 按文件类型分组统计
        type_stats = {}
        for result in results:
            file_type = result.file_type.value
            if file_type not in type_stats:
                type_stats[file_type] = {"total": 0, "success": 0}
            type_stats[file_type]["total"] += 1
            if result.success:
                type_stats[file_type]["success"] += 1
        
        print("\n按类型统计:")
        for file_type, stats in type_stats.items():
            success_rate = stats["success"] / stats["total"] * 100
            print(f"  {file_type}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
    
    # 自定义解析配置
    print("\n自定义解析配置:")
    
    # 只解析特定类型的文件
    pdf_files = [f for f in Path(".").glob("*.pdf") if f.exists()]
    if pdf_files:
        print(f"解析 PDF 文件: {[f.name for f in pdf_files]}")
        pdf_results = await parser.parse_files(pdf_files)
        
        for result in pdf_results:
            if result.success:
                # 获取 PDF 特定信息
                page_count = result.metadata.get("page_count", 0)
                has_ocr = result.metadata.get("has_ocr_content", False)
                print(f"  {result.filename}: {page_count} 页, OCR: {'是' if has_ocr else '否'}")
    
    # 错误处理示例
    print("\n错误处理示例:")
    
    # 尝试解析不存在的文件
    result = await parser.parse_file("nonexistent.pdf")
    print(f"不存在文件: 成功={result.success}, 错误={result.error_message}")
    
    # 尝试解析不支持的文件类型
    result = await parser.parse_file("test.unknown")
    print(f"不支持类型: 成功={result.success}, 错误={result.error_message}")
    
    # 获取解析器详细信息
    print("\n解析器信息:")
    info = parser.get_parser_info()
    print(f"支持的类型: {info['supported_types']}")
    print(f"支持的扩展名: {info['supported_extensions']}")


if __name__ == "__main__":
    asyncio.run(main())

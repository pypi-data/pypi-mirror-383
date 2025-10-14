"""
基本使用示例
"""

import asyncio
from pathlib import Path
from file_parser import FileParser


async def main():
    """基本使用示例"""
    # 创建解析器实例
    parser = FileParser()
    
    # 显示支持的格式
    print("支持的文件格式:")
    print(f"  扩展名: {parser.get_supported_extensions()}")
    print(f"  类型: {[t.value for t in parser.get_supported_types()]}")
    print()
    
    # 示例文件路径（请替换为实际文件路径）
    sample_files = [
        "sample.pdf",
        "sample.docx", 
        "sample.xlsx",
        "sample.png",
        "sample.txt"
    ]
    
    # 检查文件是否存在
    existing_files = [f for f in sample_files if Path(f).exists()]
    
    if not existing_files:
        print("没有找到示例文件，请将文件放在当前目录下")
        print("支持的示例文件名:", sample_files)
        return
    
    print(f"找到 {len(existing_files)} 个文件，开始解析...")
    print()
    
    # 解析单个文件
    for file_path in existing_files[:1]:  # 只解析第一个文件作为示例
        print(f"解析文件: {file_path}")
        result = await parser.parse_file(file_path)
        
        print(f"  成功: {result.success}")
        print(f"  类型: {result.file_type.value}")
        print(f"  处理时间: {result.processing_time:.2f}s")
        
        if result.success:
            print(f"  内容预览: {result.text[:200]}...")
        else:
            print(f"  错误: {result.error_message}")
        print()
    
    # 批量解析
    if len(existing_files) > 1:
        print("批量解析文件...")
        results = await parser.parse_files(existing_files)
        
        success_count = sum(1 for r in results if r.success)
        print(f"批量解析完成: 成功 {success_count}/{len(results)}")
        
        for result in results:
            status = "✓" if result.success else "✗"
            print(f"  {status} {result.filename} ({result.file_type.value})")


if __name__ == "__main__":
    asyncio.run(main())

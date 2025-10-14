"""
命令行接口
"""

import asyncio
import argparse
import json
from pathlib import Path
from typing import List
from loguru import logger

from .file_parser import FileParser


def setup_logging(verbose: bool = False):
    """设置日志"""
    if verbose:
        logger.add("file_parser.log", level="DEBUG", rotation="10 MB")
    else:
        logger.add("file_parser.log", level="INFO", rotation="10 MB")


async def parse_files_cli(file_paths: List[str], output_file: str = None, 
                         max_concurrent: int = 5, verbose: bool = False):
    """解析文件的命令行接口"""
    setup_logging(verbose)
    
    parser = FileParser(max_concurrent=max_concurrent)
    
    # 检查文件是否存在
    existing_files = [f for f in file_paths if Path(f).exists()]
    if not existing_files:
        print("错误: 没有找到任何文件")
        return
    
    print(f"开始解析 {len(existing_files)} 个文件...")
    
    # 解析文件
    results = await parser.parse_files(existing_files)
    
    # 统计结果
    success_count = sum(1 for r in results if r.success)
    print(f"解析完成: 成功 {success_count}/{len(results)}")
    
    # 输出结果
    if output_file:
        # 保存到文件
        output_data = []
        for result in results:
            output_data.append({
                "filename": result.filename,
                "file_type": result.file_type.value,
                "success": result.success,
                "text": result.text,
                "metadata": result.metadata,
                "error_message": result.error_message,
                "processing_time": result.processing_time
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {output_file}")
    else:
        # 打印到控制台
        for result in results:
            status = "✓" if result.success else "✗"
            print(f"\n{status} {result.filename} ({result.file_type.value})")
            if result.success:
                print(f"  内容: {result.text[:200]}...")
            else:
                print(f"  错误: {result.error_message}")


async def parse_directory_cli(directory: str, output_file: str = None,
                            recursive: bool = True, patterns: List[str] = None,
                            max_concurrent: int = 5, verbose: bool = False):
    """解析目录的命令行接口"""
    setup_logging(verbose)
    
    parser = FileParser(max_concurrent=max_concurrent)
    
    if not Path(directory).exists():
        print(f"错误: 目录不存在: {directory}")
        return
    
    print(f"解析目录: {directory}")
    
    # 解析目录
    results = await parser.parse_directory(
        directory,
        recursive=recursive,
        file_patterns=patterns
    )
    
    if not results:
        print("目录中没有找到支持的文件")
        return
    
    # 统计结果
    success_count = sum(1 for r in results if r.success)
    print(f"解析完成: 成功 {success_count}/{len(results)}")
    
    # 输出结果
    if output_file:
        # 保存到文件
        output_data = []
        for result in results:
            output_data.append({
                "filename": result.filename,
                "file_type": result.file_type.value,
                "success": result.success,
                "text": result.text,
                "metadata": result.metadata,
                "error_message": result.error_message,
                "processing_time": result.processing_time
            })
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"结果已保存到: {output_file}")
    else:
        # 打印统计信息
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


def show_info():
    """显示解析器信息"""
    parser = FileParser()
    info = parser.get_parser_info()
    
    print("文件解析器信息:")
    print(f"  支持的类型: {', '.join(info['supported_types'])}")
    print(f"  支持的扩展名: {', '.join(info['supported_extensions'])}")
    print("\n解析器详情:")
    for file_type, parser_info in info['parsers'].items():
        print(f"  {file_type}:")
        print(f"    类名: {parser_info['class']}")
        print(f"    扩展名: {', '.join(parser_info['extensions'])}")
        print(f"    描述: {parser_info['description']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="文件解析器命令行工具")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 解析文件命令
    parse_files_parser = subparsers.add_parser("parse", help="解析文件")
    parse_files_parser.add_argument("files", nargs="+", help="要解析的文件路径")
    parse_files_parser.add_argument("-o", "--output", help="输出文件路径")
    parse_files_parser.add_argument("-c", "--concurrent", type=int, default=5, help="最大并发数")
    parse_files_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    # 解析目录命令
    parse_dir_parser = subparsers.add_parser("parse-dir", help="解析目录")
    parse_dir_parser.add_argument("directory", help="要解析的目录路径")
    parse_dir_parser.add_argument("-o", "--output", help="输出文件路径")
    parse_dir_parser.add_argument("-r", "--recursive", action="store_true", default=True, help="递归搜索子目录")
    parse_dir_parser.add_argument("-p", "--patterns", nargs="+", help="文件模式，如 *.pdf *.docx")
    parse_dir_parser.add_argument("-c", "--concurrent", type=int, default=5, help="最大并发数")
    parse_dir_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    # 显示信息命令
    subparsers.add_parser("info", help="显示解析器信息")
    
    args = parser.parse_args()
    
    if args.command == "parse":
        asyncio.run(parse_files_cli(
            args.files,
            args.output,
            args.concurrent,
            args.verbose
        ))
    elif args.command == "parse-dir":
        asyncio.run(parse_directory_cli(
            args.directory,
            args.output,
            args.recursive,
            args.patterns,
            args.concurrent,
            args.verbose
        ))
    elif args.command == "info":
        show_info()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

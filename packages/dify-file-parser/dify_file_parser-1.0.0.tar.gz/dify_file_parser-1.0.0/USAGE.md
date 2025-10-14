# 使用指南

## 快速开始

### 基本使用

```python
import asyncio
from file_parser import FileParser

async def main():
    # 创建解析器
    parser = FileParser()
    
    # 解析单个文件
    result = await parser.parse_file("document.pdf")
    
    if result.success:
        print(f"文件内容: {result.text}")
    else:
        print(f"解析失败: {result.error_message}")

# 运行
asyncio.run(main())
```

### 批量解析

```python
import asyncio
from file_parser import FileParser

async def main():
    parser = FileParser()
    
    # 批量解析文件
    files = ["doc1.pdf", "doc2.docx", "image.png"]
    results = await parser.parse_files(files)
    
    for result in results:
        print(f"{result.filename}: {'成功' if result.success else '失败'}")

asyncio.run(main())
```

## 高级用法

### 解析目录

```python
import asyncio
from file_parser import FileParser

async def main():
    parser = FileParser()
    
    # 解析整个目录
    results = await parser.parse_directory(
        "documents/",
        recursive=True,  # 递归搜索子目录
        file_patterns=["*.pdf", "*.docx"]  # 只解析特定格式
    )
    
    print(f"解析了 {len(results)} 个文件")

asyncio.run(main())
```

### 自定义配置

```python
import asyncio
from file_parser import FileParser

async def main():
    # 设置最大并发数
    parser = FileParser(max_concurrent=3)
    
    # 解析文件
    result = await parser.parse_file("document.pdf")
    
    # 获取详细信息
    print(f"文件类型: {result.file_type.value}")
    print(f"处理时间: {result.processing_time:.2f}秒")
    print(f"元数据: {result.metadata}")

asyncio.run(main())
```

## 命令行使用

### 解析单个文件

```bash
# 解析文件并输出到控制台
file-parser parse document.pdf

# 解析文件并保存结果
file-parser parse document.pdf -o result.json

# 详细输出
file-parser parse document.pdf -v
```

### 解析目录

```bash
# 解析目录
file-parser parse-dir documents/

# 只解析特定格式
file-parser parse-dir documents/ -p "*.pdf" "*.docx"

# 递归搜索并保存结果
file-parser parse-dir documents/ -r -o results.json
```

### 查看支持格式

```bash
# 显示支持的格式
file-parser info
```

## 支持的文件格式

### PDF 文件
- 支持文本提取
- 支持 OCR 识别（图片中的文字）
- 自动检测页面数量

```python
result = await parser.parse_file("document.pdf")
print(f"页数: {result.metadata.get('page_count', 0)}")
print(f"包含 OCR 内容: {result.metadata.get('has_ocr_content', False)}")
```

### Word 文档
- 支持 .docx 和 .doc 格式
- 提取段落和表格内容
- 保持文档结构

```python
result = await parser.parse_file("document.docx")
print(f"段落数: {result.metadata.get('paragraph_count', 0)}")
```

### Excel 表格
- 支持 .xlsx 和 .xls 格式
- 提取所有工作表数据
- 保持表格结构

```python
result = await parser.parse_file("spreadsheet.xlsx")
print(f"工作表数: {result.metadata.get('sheet_count', 0)}")
for sheet in result.metadata.get('sheets', []):
    print(f"工作表 {sheet['name']}: {sheet['rows']} 行 {sheet['columns']} 列")
```

### PowerPoint 演示文稿
- 支持 .pptx 和 .ppt 格式
- 提取幻灯片内容
- 保持标题和内容结构

```python
result = await parser.parse_file("presentation.pptx")
print(f"幻灯片数: {result.metadata.get('slide_count', 0)}")
```

### 图片文件
- 支持多种格式：JPG、PNG、BMP、TIFF 等
- 使用 OCR 识别文字
- 自动图片预处理

```python
result = await parser.parse_file("image.png")
print(f"图片尺寸: {result.metadata.get('image_info', {}).get('width', 0)}x{result.metadata.get('image_info', {}).get('height', 0)}")
print(f"OCR 置信度: {result.metadata.get('ocr_confidence', 0)}")
```

### 文本文件
- 支持 .txt、.md、.log 等格式
- 自动检测编码
- 支持 Markdown 转换

```python
result = await parser.parse_file("document.txt")
print(f"编码: {result.metadata.get('encoding', 'unknown')}")
print(f"字符数: {result.metadata.get('stats', {}).get('char_count', 0)}")
```

### CSV 文件
- 自动检测分隔符和编码
- 提取表格数据
- 保持行列结构

```python
result = await parser.parse_file("data.csv")
print(f"行数: {result.metadata.get('stats', {}).get('row_count', 0)}")
print(f"列数: {result.metadata.get('stats', {}).get('column_count', 0)}")
```

## 错误处理

### 常见错误类型

1. **文件不存在**
```python
result = await parser.parse_file("nonexistent.pdf")
if not result.success:
    print(f"错误: {result.error_message}")
```

2. **不支持的文件格式**
```python
result = await parser.parse_file("file.unknown")
if not result.success:
    print(f"错误: {result.error_message}")
```

3. **解析失败**
```python
result = await parser.parse_file("corrupted.pdf")
if not result.success:
    print(f"解析失败: {result.error_message}")
```

### 批量处理错误

```python
results = await parser.parse_files(["file1.pdf", "file2.docx", "file3.unknown"])

for result in results:
    if result.success:
        print(f"✓ {result.filename}: 解析成功")
    else:
        print(f"✗ {result.filename}: {result.error_message}")
```

## 性能优化

### 并发控制

```python
# 根据系统资源调整并发数
parser = FileParser(max_concurrent=5)  # 默认值
```

### 内存管理

```python
# 处理大文件时减少并发数
parser = FileParser(max_concurrent=1)

# 分批处理大量文件
files = ["file1.pdf", "file2.pdf", ...]  # 大量文件
batch_size = 10

for i in range(0, len(files), batch_size):
    batch = files[i:i + batch_size]
    results = await parser.parse_files(batch)
    # 处理结果...
```

## 扩展开发

### 添加新的文件类型

```python
from file_parser.base import BaseParser, ParseResult, FileType

class CustomParser(BaseParser):
    @property
    def supported_extensions(self):
        return [".custom"]
    
    @property
    def file_type(self):
        return FileType.UNKNOWN  # 或定义新的类型
    
    async def parse(self, file_path):
        # 实现解析逻辑
        return ParseResult(
            filename=Path(file_path).name,
            file_type=self.file_type,
            text="解析的内容",
            metadata={},
            success=True
        )
```

### 自定义 OCR 配置

```python
from file_parser.ocr.tesseract_ocr import TesseractOCR

# 创建自定义 OCR 实例
ocr = TesseractOCR(lang="chi_sim+eng")

# 在图片解析器中使用
from file_parser.parsers.image_parser import ImageParser
parser = ImageParser()
parser.ocr = ocr
```

## 最佳实践

1. **异步使用**：始终使用 `async/await` 语法
2. **错误处理**：检查 `result.success` 状态
3. **资源管理**：处理大量文件时分批进行
4. **日志记录**：使用 `loguru` 记录处理过程
5. **测试覆盖**：为自定义解析器编写测试

## 故障排除

### 常见问题

1. **Tesseract 未安装**：按照安装指南安装 OCR 依赖
2. **内存不足**：减少并发数或分批处理
3. **编码问题**：确保文件使用正确编码
4. **权限问题**：确保有文件读取权限

### 调试技巧

```python
import logging
from loguru import logger

# 启用详细日志
logger.add("debug.log", level="DEBUG")

# 在代码中添加调试信息
logger.debug(f"正在解析文件: {file_path}")
```

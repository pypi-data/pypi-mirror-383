# 文件解析器 (File Parser)

一个基于 Dify 项目文件处理功能抽离的通用文件解析器，支持多种文件格式转换为 AI 可识别的文本。

## 功能特性

- 📄 支持多种文件格式：PDF、Word、Excel、PowerPoint、图片、文本等
- 🔍 集成 OCR 技术，支持图片文字识别
- 🚀 高性能异步处理
- 🔧 模块化设计，易于扩展
- 📝 统一的文本输出格式
- 🛡️ 错误处理和日志记录

## 支持的文件格式

| 格式 | 扩展名 | 状态 | 说明 |
|------|--------|------|------|
| PDF | .pdf | ✅ | 支持文本提取和 OCR |
| Word | .docx, .doc | ✅ | 支持文档内容提取 |
| Excel | .xlsx, .xls | ✅ | 支持表格数据提取 |
| PowerPoint | .pptx, .ppt | ✅ | 支持幻灯片内容提取 |
| 图片 | .jpg, .jpeg, .png, .bmp, .tiff | ✅ | 支持 OCR 文字识别 |
| 文本 | .txt, .md | ✅ | 直接文本读取 |
| CSV | .csv | ✅ | 表格数据解析 |

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from file_parser import FileParser

# 创建解析器实例
parser = FileParser()

# 解析单个文件
result = await parser.parse_file("document.pdf")
print(result.text)

# 批量解析文件
files = ["doc1.pdf", "doc2.docx", "image.png"]
results = await parser.parse_files(files)
for result in results:
    print(f"文件: {result.filename}")
    print(f"内容: {result.text[:100]}...")
```

## 项目结构

```
file-parser/
├── file_parser/           # 核心模块
│   ├── __init__.py
│   ├── base.py           # 基础解析器类
│   ├── parsers/          # 具体解析器实现
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── word_parser.py
│   │   ├── excel_parser.py
│   │   ├── ppt_parser.py
│   │   ├── image_parser.py
│   │   └── text_parser.py
│   ├── ocr/              # OCR 相关功能
│   │   ├── __init__.py
│   │   └── tesseract_ocr.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       └── file_utils.py
├── tests/                # 测试文件
├── examples/             # 示例代码
├── requirements.txt      # 依赖列表
└── README.md
```

## 许可证

MIT License

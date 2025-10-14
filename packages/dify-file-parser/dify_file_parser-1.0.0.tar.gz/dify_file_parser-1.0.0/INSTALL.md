# 安装指南

## 系统要求

- Python 3.8 或更高版本
- 操作系统：Windows、macOS、Linux

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/javen-yan/file-parser.git
cd file-parser
```

### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装基本依赖
pip install -r requirements.txt

# 或者使用 pip 安装
pip install -e .
```

### 4. 安装 OCR 依赖（可选）

如果要使用图片 OCR 功能，需要安装 Tesseract OCR：

#### Windows
1. 下载 Tesseract 安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装后添加到系统 PATH
3. 安装 Python 依赖：
```bash
pip install pytesseract opencv-python
```

#### macOS
```bash
# 使用 Homebrew
brew install tesseract tesseract-lang

# 安装 Python 依赖
pip install pytesseract opencv-python
```

#### Ubuntu/Debian
```bash
# 安装 Tesseract
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim

# 安装 Python 依赖
pip install pytesseract opencv-python
```

#### CentOS/RHEL
```bash
# 安装 Tesseract
sudo yum install tesseract tesseract-langpack-chi-sim

# 安装 Python 依赖
pip install pytesseract opencv-python
```

## 验证安装

```bash
# 运行测试
pytest

# 查看支持的文件格式
python -m file_parser.cli info

# 测试基本功能
python examples/basic_usage.py
```

## 开发环境设置

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行代码检查
flake8 file_parser/
black file_parser/
mypy file_parser/

# 运行测试
pytest --cov=file_parser
```

## 常见问题

### 1. Tesseract 未找到

如果遇到 "TesseractNotFoundError"，请确保：
- Tesseract 已正确安装
- Tesseract 在系统 PATH 中
- 或者设置环境变量：
```python
from file_parser.ocr.tesseract_ocr import TesseractOCR
ocr = TesseractOCR(tesseract_cmd="/path/to/tesseract")
```

### 2. 内存不足

处理大文件时可能遇到内存问题，可以：
- 减少并发数：`FileParser(max_concurrent=1)`
- 分批处理文件
- 增加系统内存

### 3. 编码问题

如果遇到文件编码问题：
- 确保文件使用 UTF-8 编码
- 对于其他编码，解析器会自动检测
- 可以手动指定编码（在具体解析器中）

## 卸载

```bash
# 卸载包
pip uninstall file-parser

# 删除虚拟环境
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

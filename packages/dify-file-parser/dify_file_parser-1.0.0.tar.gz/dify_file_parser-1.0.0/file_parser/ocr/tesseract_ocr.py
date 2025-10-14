"""
基于 Tesseract 的 OCR 实现
"""

import pytesseract
from PIL import Image
from typing import Dict, Any, Optional, List, Union
import re
from loguru import logger


class TesseractOCR:
    """Tesseract OCR 实现"""
    
    def __init__(self, tesseract_cmd: Optional[str] = None, lang: str = 'chi_sim+eng'):
        """
        初始化 OCR 引擎
        
        Args:
            tesseract_cmd: Tesseract 可执行文件路径
            lang: 语言设置，默认中英文
        """
        self.logger = logger.bind(ocr="TesseractOCR")
        
        # 设置 Tesseract 路径（如果需要）
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        
        self.lang = lang
        self.available_languages = []
        self._check_tesseract_installation()
        self._check_chinese_support()
    
    def _check_tesseract_installation(self):
        """检查 Tesseract 是否正确安装"""
        try:
            # 尝试获取版本信息
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"Tesseract 版本: {version}")
            
            # 获取可用语言列表
            self.available_languages = self.get_available_languages()
            
        except Exception as e:
            self.logger.warning(f"Tesseract 可能未正确安装: {str(e)}")
            self.logger.warning("请安装 Tesseract OCR: https://github.com/tesseract-ocr/tesseract")
    
    def _check_chinese_support(self):
        """检查中文支持"""
        chinese_langs = ['chi_sim', 'chi_tra', 'chi_sim_vert', 'chi_tra_vert']
        available_chinese = [lang for lang in chinese_langs if lang in self.available_languages]
        
        if not available_chinese:
            self.logger.warning("未检测到中文语言包！")
            self.logger.warning("请安装中文语言包:")
            self.logger.warning("  Ubuntu/Debian: sudo apt-get install tesseract-ocr-chi-sim")
            self.logger.warning("  CentOS/RHEL: sudo yum install tesseract-langpack-chi_sim")
            self.logger.warning("  macOS: brew install tesseract-lang")
            self.logger.warning("  Windows: 下载中文语言包到 tessdata 目录")
            
            # 如果没有中文支持，回退到英文
            if 'eng' in self.available_languages:
                self.lang = 'eng'
                self.logger.warning(f"回退到英文识别: {self.lang}")
            else:
                self.logger.error("没有可用的语言包！")
        else:
            self.logger.info(f"检测到中文语言包: {available_chinese}")
            # 优先使用简体中文
            if 'chi_sim' in available_chinese:
                self.lang = 'chi_sim+eng'
            elif 'chi_tra' in available_chinese:
                self.lang = 'chi_tra+eng'
            else:
                self.lang = available_chinese[0] + '+eng'
            
            self.logger.info(f"使用语言设置: {self.lang}")
    
    def extract_text(self, image: Union[str, Image.Image], config: Optional[str] = None) -> str:
        """
        从图片中提取文字
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: Tesseract 配置参数
            
        Returns:
            str: 提取的文字
        """
        try:
            if config is None:
                # 针对中文优化的配置
                config = self._get_optimized_config()
            
            # 处理图片输入
            if isinstance(image, str):
                # 如果是路径，直接使用路径
                text = pytesseract.image_to_string(image, lang=self.lang, config=config)
            else:
                # 如果是PIL Image，使用image_to_string
                text = pytesseract.image_to_string(image, lang=self.lang, config=config)
            
            # 清理文字
            cleaned_text = self._clean_text(text)
            
            self.logger.debug(f"OCR 提取文字长度: {len(cleaned_text)}")
            return cleaned_text
            
        except Exception as e:
            self.logger.error(f"OCR 文字提取失败: {str(e)}")
            return f"[OCR 错误: {str(e)}]"
    
    def _get_optimized_config(self) -> str:
        """获取针对中文优化的配置"""
        # 基础配置
        base_config = "--oem 3 --psm 6"
        
        # 中文特定优化
        chinese_optimizations = [
            "--user-words",  # 用户词典
            "--user-patterns",  # 用户模式
            "--tessdata-dir",  # 数据目录
        ]
        
        # 构建完整配置
        config_parts = [base_config]
        
        # 添加语言设置
        config_parts.append(f"-l {self.lang}")
        
        # 添加中文优化参数
        if 'chi' in self.lang:
            # 针对中文的额外优化
            config_parts.extend([
                "--psm 6",  # 统一文本块
                "--oem 3",  # 默认LSTM OCR引擎模式
            ])
        
        return " ".join(config_parts)
    
    def extract_text_with_confidence(self, image: Union[str, Image.Image], config: Optional[str] = None) -> Dict[str, Any]:
        """
        从图片中提取文字并返回置信度信息
        
        Args:
            image: 图片路径字符串或PIL Image 对象
            config: Tesseract 配置参数
            
        Returns:
            Dict[str, Any]: 包含文字和置信度的字典
        """
        try:
            if config is None:
                config = self._get_optimized_config()
            
            # 处理图片输入
            if isinstance(image, str):
                # 如果是路径，直接使用路径
                data = pytesseract.image_to_data(image, lang=self.lang, config=config, output_type=pytesseract.Output.DICT)
                text = pytesseract.image_to_string(image, lang=self.lang, config=config)
            else:
                # 如果是PIL Image，使用image_to_data和image_to_string
                data = pytesseract.image_to_data(image, lang=self.lang, config=config, output_type=pytesseract.Output.DICT)
                text = pytesseract.image_to_string(image, lang=self.lang, config=config)
            cleaned_text = self._clean_text(text)
            
            # 计算置信度统计
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            
            if confidences:
                avg_confidence = sum(confidences) / len(confidences)
                max_confidence = max(confidences)
                min_confidence = min(confidences)
                high_conf_count = len([c for c in confidences if c > 70])
                low_conf_count = len([c for c in confidences if c < 30])
            else:
                avg_confidence = max_confidence = min_confidence = 0
                high_conf_count = low_conf_count = 0
            
            # 计算文本质量评分
            text_quality = self._calculate_text_quality(cleaned_text, confidences)
            
            return {
                "text": cleaned_text,
                "confidence": avg_confidence,
                "max_confidence": max_confidence,
                "min_confidence": min_confidence,
                "high_conf_count": high_conf_count,
                "low_conf_count": low_conf_count,
                "word_count": len(cleaned_text.split()),
                "char_count": len(cleaned_text),
                "text_quality": text_quality,
                "method": "tesseract"
            }
            
        except Exception as e:
            self.logger.error(f"OCR 文字提取失败: {str(e)}")
            return {
                "text": f"[OCR 错误: {str(e)}]",
                "confidence": 0,
                "max_confidence": 0,
                "min_confidence": 0,
                "high_conf_count": 0,
                "low_conf_count": 0,
                "word_count": 0,
                "char_count": 0,
                "text_quality": 0,
                "method": "tesseract"
            }
    
    def _calculate_text_quality(self, text: str, confidences: List[int]) -> float:
        """计算文本质量评分"""
        if not text or not confidences:
            return 0.0
        
        # 基础质量评分（基于置信度）
        avg_conf = sum(confidences) / len(confidences)
        conf_score = avg_conf / 100.0
        
        # 文本长度评分
        length_score = min(1.0, len(text) / 100.0)
        
        # 中文字符比例评分
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        chinese_ratio = chinese_chars / len(text) if text else 0
        chinese_score = chinese_ratio if 'chi' in self.lang else 1.0
        
        # 标点符号评分
        punctuation_chars = len([c for c in text if c in '。，！？；：""''（）【】《》'])
        punct_score = min(1.0, punctuation_chars / 10.0)
        
        # 综合评分
        quality = (conf_score * 0.4 + length_score * 0.2 + chinese_score * 0.2 + punct_score * 0.2)
        
        return min(1.0, quality)
    
    def _clean_text(self, text: str) -> str:
        """
        清理提取的文字，特别针对中文优化
        
        Args:
            text: 原始文字
            
        Returns:
            str: 清理后的文字
        """
        if not text:
            return ""
        
        # 移除多余的空白字符，但保留中文标点后的换行
        text = re.sub(r'[ \t]+', ' ', text)  # 多个空格/制表符合并为一个空格
        
        # 处理中文标点符号
        text = re.sub(r'([。！？；：])\s*', r'\1\n', text)  # 句号等后换行
        text = re.sub(r'([，、])\s*', r'\1 ', text)  # 逗号等后加空格
        
        # 处理英文标点
        text = re.sub(r'([.!?;:])\s*', r'\1 ', text)
        text = re.sub(r'([,;])\s*', r'\1 ', text)
        
        # 移除行首行尾空白
        lines = [line.strip() for line in text.split('\n')]
        
        # 移除空行，但保留段落分隔
        cleaned_lines = []
        for i, line in enumerate(lines):
            if line:  # 非空行
                cleaned_lines.append(line)
            elif i > 0 and cleaned_lines and cleaned_lines[-1]:  # 空行且前一行非空
                cleaned_lines.append('')  # 保留段落分隔
        
        # 重新组合
        cleaned_text = '\n'.join(cleaned_lines)
        
        # 最终清理
        cleaned_text = cleaned_text.strip()
        
        # 移除重复的换行
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)
        
        return cleaned_text
    
    def get_available_languages(self) -> list:
        """
        获取可用的语言列表
        
        Returns:
            list: 可用语言列表
        """
        try:
            langs = pytesseract.get_languages()
            self.logger.info(f"可用语言: {langs}")
            return langs
        except Exception as e:
            self.logger.error(f"获取语言列表失败: {str(e)}")
            return []
    
    def set_language(self, lang: str):
        """
        设置 OCR 语言
        
        Args:
            lang: 语言代码，如 'chi_sim+eng'
        """
        self.lang = lang
        self.logger.info(f"设置 OCR 语言为: {lang}")

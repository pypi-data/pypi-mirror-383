"""
文件工具函数
"""

import asyncio
import aiofiles
from pathlib import Path
from typing import List, Dict, Any, Optional
import mimetypes
import hashlib
from loguru import logger


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_file_extension(file_path: str) -> str:
        """
        获取文件扩展名
        
        Args:
            file_path: 文件路径
            
        Returns:
            str: 文件扩展名（小写）
        """
        return Path(file_path).suffix.lower()
    
    @staticmethod
    def get_mime_type(file_path: str) -> Optional[str]:
        """
        获取文件 MIME 类型
        
        Args:
            file_path: 文件路径
            
        Returns:
            Optional[str]: MIME 类型
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type
    
    @staticmethod
    async def get_file_size(file_path: str) -> int:
        """
        获取文件大小
        
        Args:
            file_path: 文件路径
            
        Returns:
            int: 文件大小（字节）
        """
        try:
            stat = await aiofiles.os.stat(file_path)
            return stat.st_size
        except Exception as e:
            logger.error(f"获取文件大小失败: {str(e)}")
            return 0
    
    @staticmethod
    async def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> Optional[str]:
        """
        计算文件哈希值
        
        Args:
            file_path: 文件路径
            algorithm: 哈希算法 ('md5', 'sha1', 'sha256')
            
        Returns:
            Optional[str]: 哈希值
        """
        try:
            hash_obj = hashlib.new(algorithm)
            
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
            
        except Exception as e:
            logger.error(f"计算文件哈希失败: {str(e)}")
            return None
    
    @staticmethod
    def is_supported_file(file_path: str, supported_extensions: List[str]) -> bool:
        """
        检查文件是否被支持
        
        Args:
            file_path: 文件路径
            supported_extensions: 支持的扩展名列表
            
        Returns:
            bool: 是否支持
        """
        extension = FileUtils.get_file_extension(file_path)
        return extension in supported_extensions
    
    @staticmethod
    async def read_file_chunk(file_path: str, chunk_size: int = 8192) -> List[bytes]:
        """
        分块读取文件
        
        Args:
            file_path: 文件路径
            chunk_size: 块大小
            
        Returns:
            List[bytes]: 文件块列表
        """
        chunks = []
        try:
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(chunk_size):
                    chunks.append(chunk)
        except Exception as e:
            logger.error(f"分块读取文件失败: {str(e)}")
        
        return chunks
    
    @staticmethod
    async def write_text_file(file_path: str, content: str, encoding: str = 'utf-8') -> bool:
        """
        写入文本文件
        
        Args:
            file_path: 文件路径
            content: 文件内容
            encoding: 编码格式
            
        Returns:
            bool: 是否成功
        """
        try:
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            return True
        except Exception as e:
            logger.error(f"写入文件失败: {str(e)}")
            return False
    
    @staticmethod
    async def ensure_directory(directory_path: str) -> bool:
        """
        确保目录存在
        
        Args:
            directory_path: 目录路径
            
        Returns:
            bool: 是否成功
        """
        try:
            Path(directory_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"创建目录失败: {str(e)}")
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict[str, Any]:
        """
        获取文件基本信息
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 文件信息
        """
        path = Path(file_path)
        
        try:
            stat = path.stat()
            return {
                "filename": path.name,
                "extension": path.suffix.lower(),
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "ctime": stat.st_ctime,
                "is_file": path.is_file(),
                "is_dir": path.is_dir(),
                "exists": path.exists()
            }
        except Exception as e:
            logger.error(f"获取文件信息失败: {str(e)}")
            return {
                "filename": path.name,
                "extension": path.suffix.lower(),
                "size": 0,
                "mtime": 0,
                "ctime": 0,
                "is_file": False,
                "is_dir": False,
                "exists": False,
                "error": str(e)
            }
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            filename: 原始文件名
            
        Returns:
            str: 清理后的文件名
        """
        import re
        
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # 移除多余的空格和点
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = filename.strip('.')
        
        # 限制长度
        if len(filename) > 255:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            filename = name[:255-len(ext)-1] + ('.' + ext if ext else '')
        
        return filename or "unnamed_file"

# utils/encoding_detector.py
import re
import chardet
from typing import Optional

class EncodingDetector:
    """网页编码自动检测器"""
    
    @staticmethod
    def detect(response_content: bytes, content_type: Optional[str] = None) -> str:
        """
        检测网页编码的优先级：
        1. HTTP头中的Content-Type
        2. HTML meta标签声明的编码
        3. chardet自动检测
        4. 默认返回utf-8
        """
        encoding = None
        
        # 1. 从HTTP头检测
        if content_type:
            encoding = EncodingDetector._get_encoding_from_header(content_type)
            if encoding:
                return encoding

        # 2. 从HTML meta标签检测
        encoding = EncodingDetector._get_encoding_from_meta(response_content)
        if encoding:
            return encoding

        # 3. 使用chardet检测
        try:
            result = chardet.detect(response_content)
            if result['confidence'] > 0.7:  # 置信度阈值
                return result['encoding'].lower()
        except Exception:
            pass

        # 4. 默认编码
        return 'utf-8'

    @staticmethod
    def _get_encoding_from_header(content_type: str) -> Optional[str]:
        """从Content-Type头提取编码"""
        match = re.search(r'charset=([\w-]+)', content_type)
        if match:
            encoding = match.group(1).lower()
            return EncodingDetector._normalize_encoding(encoding)
        return None

    @staticmethod
    def _get_encoding_from_meta(content: bytes, sample_size: int = 1024) -> Optional[str]:
        """从HTML meta标签提取编码"""
        # 只检查前1KB内容以提高效率
        sample = content[:sample_size].decode('ascii', errors='ignore')
        
        # 检查HTML5的<meta charset="...">
        meta_charset = re.search(
            r'<meta\s+charset=["\']?([\w-]+)["\']?', 
            sample, 
            re.IGNORECASE
        )
        if meta_charset:
            return EncodingDetector._normalize_encoding(meta_charset.group(1))

        # 检查旧式<meta http-equiv="Content-Type">
        meta_http_equiv = re.search(
            r'<meta\s+http-equiv=["\']?Content-Type["\']?.*content=["\'][^"\']*charset=([\w-]+)',
            sample,
            re.IGNORECASE
        )
        if meta_http_equiv:
            return EncodingDetector._normalize_encoding(meta_http_equiv.group(1))

        return None

    @staticmethod
    def _normalize_encoding(encoding: str) -> str:
        """标准化编码名称"""
        encoding = encoding.lower()
        encoding_map = {
            'gb2312': 'gb18030',
            'gbk': 'gb18030',
            'utf8': 'utf-8',
            'ascii': 'utf-8'
        }
        return encoding_map.get(encoding, encoding)

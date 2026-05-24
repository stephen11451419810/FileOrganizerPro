"""
文件分类器 - 多种分类策略
"""

import re
from pathlib import Path
from typing import Dict, Optional

try:
    from pypdf2 import PdfReader
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

from src.utils import get_logger


class NameClassifier:
    def __init__(self, config: dict):
        self.keyword_map = {
            '发票': '发票', 'invoice': '发票', '账单': '发票',
            '报告': '文档', '说明': '文档', '文档': '文档',
            '照片': '图片', '图片': '图片', 'IMG_': '图片',
            '视频': '视频', '录像': '视频', '代码': '代码'
        }
    
    def classify(self, file_path: Path) -> str:
        name_lower = file_path.stem.lower()
        for keyword, category in self.keyword_map.items():
            if keyword.lower() in name_lower:
                return category
        return '其他'


class ExtensionClassifier:
    def __init__(self, categories: Dict):
        self.reverse_map = {}
        for category, extensions in categories.items():
            for ext in extensions:
                self.reverse_map[ext.lower()] = category
    
    def classify(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        return self.reverse_map.get(ext, '其他')


class ContentClassifier:
    def __init__(self, config: dict):
        self.config = config
    
    def classify(self, file_path: Path) -> str:
        ext = file_path.suffix.lower()
        
        if ext in ['.txt', '.md', '.log']:
            return '文档'
        
        if ext == '.pdf' and PDF_AVAILABLE:
            try:
                reader = PdfReader(file_path)
                if len(reader.pages) > 0:
                    text = reader.pages[0].extract_text()[:200]
                    if '发票' in text or 'invoice' in text.lower():
                        return '发票'
                return '文档'
            except:
                pass
        
        if ext in ['.docx', '.doc'] and DOCX_AVAILABLE:
            try:
                doc = Document(file_path)
                text = '\n'.join([p.text for p in doc.paragraphs[:5]])
                if '发票' in text or 'invoice' in text.lower():
                    return '发票'
                return '文档'
            except:
                pass
        
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            return '图片'
        if ext in ['.mp4', '.avi', '.mov', '.mkv', '.flv']:
            return '视频'
        if ext in ['.mp3', '.wav', '.flac', '.aac', '.m4a']:
            return '音频'
        if ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.go']:
            return '代码'
        if ext in ['.zip', '.rar', '.7z', '.tar', '.gz']:
            return '压缩包'
        
        return '其他'


class AIClassifier:
    def __init__(self, config: dict):
        self.config = config
        self.enabled = config.get('enabled', False)
        self.logger = get_logger()
    
    def is_available(self) -> bool:
        return self.enabled and self.config.get('api_key') is not None
    
    def classify(self, file_path: Path) -> str:
        if not self.is_available():
            return '其他'
        return self.classifiers.get('extension').classify(file_path)

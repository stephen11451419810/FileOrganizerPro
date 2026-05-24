"""
工具函数模块
"""

import logging
import json
from pathlib import Path
from typing import Optional


def setup_logger(name: str = "FileOrganizer") -> logging.Logger:
    """设置日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_logger() -> logging.Logger:
    """获取日志记录器"""
    return logging.getLogger("FileOrganizer")


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "config/default_rules.json"
    
    def load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "categories": {},
            "invoice_keywords": ["发票", "invoice"],
            "ignore_extensions": [],
            "ignore_folders": [],
            "special_rules": {"generate_report": True}
        }
        
        try:
            path = Path(self.config_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
        except Exception as e:
            get_logger().warning(f"加载配置文件失败: {str(e)}")
        
        return default_config


class FileUtils:
    """文件工具类"""
    
    @staticmethod
    def get_file_size_str(size_bytes: int) -> str:
        """获取可读的文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

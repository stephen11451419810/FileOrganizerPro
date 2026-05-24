"""
核心整理器 - 负责文件的整体组织逻辑
"""

import os
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from collections import defaultdict

from src.classifiers import NameClassifier, ExtensionClassifier, ContentClassifier, AIClassifier
from src.utils import get_logger


class FileOrganizer:
    """文件整理器主类"""
    
    def __init__(self, target_dir: Path, mode: str = 'auto', 
                 recursive: bool = False, preview: bool = False, 
                 config: dict = None):
        self.target_dir = Path(target_dir)
        self.mode = mode
        self.recursive = recursive
        self.preview = preview
        self.config = config or {}
        self.logger = get_logger()
        
        self.categories = self.config.get('categories', {})
        self.invoice_keywords = self.config.get('invoice_keywords', 
            ['发票', 'invoice', 'fapiao', '账单'])
        self.ignore_extensions = self.config.get('ignore_extensions', [])
        self.ignore_folders = self.config.get('ignore_folders', [])
        
        self.classifiers = {
            'name': NameClassifier(self.config),
            'extension': ExtensionClassifier(self.categories),
            'content': ContentClassifier(self.config),
            'ai': AIClassifier(self.config.get('ai_settings', {}))
        }
        
        self.stats = {
            'target_dir': str(self.target_dir),
            'total_files': 0,
            'processed_files': 0,
            'categories': defaultdict(int),
            'errors': [],
            'start_time': datetime.now()
        }
        
        self.move_plan = []
    
    def run(self) -> Dict:
        self.logger.info(f"开始整理目录: {self.target_dir}")
        
        files = self._scan_files()
        self.stats['total_files'] = len(files)
        
        if self.stats['total_files'] == 0:
            self.logger.info("没有找到需要整理的文件")
            return self.stats
        
        for file_path in files:
            try:
                self._process_file(file_path)
            except Exception as e:
                self.stats['errors'].append(f"{file_path.name}: {str(e)}")
        
        if not self.preview and self.move_plan:
            self._execute_move_plan()
        
        report_path = self._generate_report()
        if report_path:
            self.stats['report_path'] = report_path
        
        self.stats['categories'] = dict(self.stats['categories'])
        elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        self.stats['elapsed_seconds'] = elapsed
        
        return self.stats
    
    def _scan_files(self) -> List[Path]:
        files = []
        if self.recursive:
            for root, dirs, filenames in os.walk(self.target_dir):
                dirs[:] = [d for d in dirs if d not in self.ignore_folders]
                for filename in filenames:
                    file_path = Path(root) / filename
                    if self._should_process_file(file_path):
                        files.append(file_path)
        else:
            for item in self.target_dir.iterdir():
                if item.is_file() and self._should_process_file(item):
                    files.append(item)
        return files
    
    def _should_process_file(self, file_path: Path) -> bool:
        if file_path.name.startswith('~') or file_path.name.startswith('.'):
            return False
        if file_path.suffix.lower() in self.ignore_extensions:
            return False
        if file_path.name.startswith('整理报告_'):
            return False
        return True
    
    def _process_file(self, file_path: Path):
        category = self._get_file_category(file_path)
        
        if self._is_invoice_file(file_path, category):
            category = '发票'
            date_folder = self._extract_invoice_date(file_path)
            if date_folder:
                category = f"{category}/{date_folder}"
        
        target_dir = self.target_dir / category
        target_path = target_dir / file_path.name
        target_path = self._resolve_name_conflict(target_path)
        
        self.move_plan.append({
            'source': file_path,
            'target': target_path,
            'category': category.split('/')[0]
        })
        
        main_category = category.split('/')[0]
        self.stats['categories'][main_category] += 1
        self.stats['processed_files'] += 1
        
        if not self.preview:
            target_dir.mkdir(parents=True, exist_ok=True)
    
    def _execute_move_plan(self):
        for plan in self.move_plan:
            try:
                plan['target'].parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(plan['source']), str(plan['target']))
            except Exception as e:
                self.logger.error(f"移动失败 {plan['source'].name}: {str(e)}")
    
    def _get_file_category(self, file_path: Path) -> str:
        if self.mode == 'name':
            return self.classifiers['name'].classify(file_path)
        elif self.mode == 'extension':
            return self.classifiers['extension'].classify(file_path)
        elif self.mode == 'content':
            return self.classifiers['content'].classify(file_path)
        elif self.mode == 'ai':
            return self.classifiers['ai'].classify(file_path)
        else:
            category = self.classifiers['content'].classify(file_path)
            if category != '其他':
                return category
            return self.classifiers['extension'].classify(file_path)
    
    def _is_invoice_file(self, file_path: Path, category: str) -> bool:
        if file_path.suffix.lower() not in ['.pdf', '.jpg', '.jpeg', '.png', '.ofd']:
            return False
        name_lower = file_path.stem.lower()
        for keyword in self.invoice_keywords:
            if keyword.lower() in name_lower:
                return True
        if category in ['发票', '财务', '账单']:
            return True
        return False
    
    def _extract_invoice_date(self, file_path: Path) -> Optional[str]:
        name = file_path.stem
        patterns = [r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})', r'(\d{4})(\d{2})(\d{2})']
        for pattern in patterns:
            match = re.search(pattern, name)
            if match:
                try:
                    year = match.group(1)
                    month = match.group(2).zfill(2)
                    return f"{year}-{month}"
                except:
                    pass
        return datetime.now().strftime("%Y-%m")
    
    def _resolve_name_conflict(self, target_path: Path) -> Path:
        if not target_path.exists():
            return target_path
        counter = 1
        stem = target_path.stem
        suffix = target_path.suffix
        parent = target_path.parent
        while True:
            new_name = f"{stem}_{counter}{suffix}"
            new_path = parent / new_name
            if not new_path.exists():
                return new_path
            counter += 1
    
    def _generate_report(self) -> Optional[Path]:
        if not self.config.get('special_rules', {}).get('generate_report', True):
            return None
        
        report_path = self.target_dir / f"整理报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 60 + "\n")
                f.write("文件整理报告\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"整理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"目标目录: {self.target_dir}\n")
                f.write(f"整理模式: {self.mode}\n")
                f.write(f"总文件数: {self.stats['total_files']}\n")
                f.write(f"处理文件: {self.stats['processed_files']}\n\n")
                f.write("分类统计:\n")
                for category, count in sorted(self.stats['categories'].items()):
                    f.write(f"  {category}: {count} 个文件\n")
            return report_path
        except Exception as e:
            self.logger.error(f"生成报告失败: {str(e)}")
            return None

#!/usr/bin/env python3
"""
File Organizer Pro - 智能文件整理工具（单文件版）
无需任何外部模块依赖，直接运行
"""

import os
import sys
import shutil
import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading


# ============== 工具函数 ==============
def setup_logger():
    import logging
    logger = logging.getLogger("FileOrganizer")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


logger = setup_logger()


# ============== 配置管理器 ==============
class ConfigManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or "config/default_rules.json"
    
    def load_config(self):
        default_config = {
            "categories": {
                "发票": [".pdf", ".jpg", ".jpeg", ".png"],
                "文档": [".txt", ".doc", ".docx", ".pdf", ".md"],
                "图片": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
                "视频": [".mp4", ".avi", ".mov", ".mkv"],
                "音频": [".mp3", ".wav", ".flac"],
                "代码": [".py", ".js", ".html", ".css", ".java"],
                "压缩包": [".zip", ".rar", ".7z", ".tar", ".gz"]
            },
            "invoice_keywords": ["发票", "invoice", "fapiao", "账单", "报销"],
            "ignore_extensions": [".lnk", ".ini"],
            "ignore_folders": ["__pycache__", ".git", "venv"],
            "special_rules": {"generate_report": True}
        }
        
        try:
            path = Path(self.config_path)
            if path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
        except:
            pass
        
        return default_config


# ============== 分类器 ==============
class ExtensionClassifier:
    def __init__(self, categories):
        self.reverse_map = {}
        for category, extensions in categories.items():
            for ext in extensions:
                self.reverse_map[ext.lower()] = category
    
    def classify(self, file_path):
        ext = file_path.suffix.lower()
        return self.reverse_map.get(ext, '其他')


class NameClassifier:
    def __init__(self, config):
        self.keyword_map = {
            '发票': '发票', 'invoice': '发票', '账单': '发票',
            '报告': '文档', '说明': '文档', '文档': '文档',
            '照片': '图片', '图片': '图片', 'IMG_': '图片',
            '视频': '视频', '录像': '视频', '代码': '代码'
        }
    
    def classify(self, file_path):
        name_lower = file_path.stem.lower()
        for keyword, category in self.keyword_map.items():
            if keyword.lower() in name_lower:
                return category
        return '其他'


# ============== 核心整理器 ==============
class FileOrganizer:
    def __init__(self, target_dir, mode='auto', recursive=False, preview=False, config=None):
        self.target_dir = Path(target_dir)
        self.mode = mode
        self.recursive = recursive
        self.preview = preview
        self.config = config or {}
        
        self.categories = self.config.get('categories', {})
        self.invoice_keywords = self.config.get('invoice_keywords', ['发票', 'invoice', '账单'])
        self.ignore_extensions = self.config.get('ignore_extensions', [])
        self.ignore_folders = self.config.get('ignore_folders', [])
        
        self.extension_classifier = ExtensionClassifier(self.categories)
        self.name_classifier = NameClassifier(self.config)
        
        self.stats = {
            'target_dir': str(self.target_dir),
            'total_files': 0,
            'processed_files': 0,
            'categories': defaultdict(int),
            'errors': [],
            'start_time': datetime.now()
        }
        self.move_plan = []
    
    def run(self):
        logger.info(f"开始整理目录: {self.target_dir}")
        files = self._scan_files()
        self.stats['total_files'] = len(files)
        
        if self.stats['total_files'] == 0:
            logger.info("没有找到需要整理的文件")
            return self.stats
        
        for file_path in files:
            try:
                self._process_file(file_path)
            except Exception as e:
                self.stats['errors'].append(f"{file_path.name}: {str(e)}")
        
        if not self.preview and self.move_plan:
            self._execute_move_plan()
        
        self._generate_report()
        self.stats['categories'] = dict(self.stats['categories'])
        self.stats['elapsed_seconds'] = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return self.stats
    
    def _scan_files(self):
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
    
    def _should_process_file(self, file_path):
        if file_path.name.startswith('~') or file_path.name.startswith('.'):
            return False
        if file_path.suffix.lower() in self.ignore_extensions:
            return False
        if file_path.name.startswith('整理报告_'):
            return False
        return True
    
    def _process_file(self, file_path):
        category = self._get_file_category(file_path)
        
        if self._is_invoice_file(file_path, category):
            category = '发票'
        
        target_dir = self.target_dir / category
        target_path = target_dir / file_path.name
        target_path = self._resolve_name_conflict(target_path)
        
        self.move_plan.append({'source': file_path, 'target': target_path})
        self.stats['categories'][category] += 1
        self.stats['processed_files'] += 1
        
        if not self.preview:
            target_dir.mkdir(parents=True, exist_ok=True)
    
    def _execute_move_plan(self):
        for plan in self.move_plan:
            try:
                plan['target'].parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(plan['source']), str(plan['target']))
                logger.debug(f"移动: {plan['source'].name} -> {plan['target'].parent}")
            except Exception as e:
                logger.error(f"移动失败 {plan['source'].name}: {str(e)}")
    
    def _get_file_category(self, file_path):
        if self.mode == 'name':
            return self.name_classifier.classify(file_path)
        elif self.mode == 'extension':
            return self.extension_classifier.classify(file_path)
        else:
            category = self.name_classifier.classify(file_path)
            if category != '其他':
                return category
            return self.extension_classifier.classify(file_path)
    
    def _is_invoice_file(self, file_path, category):
        if file_path.suffix.lower() not in ['.pdf', '.jpg', '.jpeg', '.png']:
            return False
        name_lower = file_path.stem.lower()
        for keyword in self.invoice_keywords:
            if keyword.lower() in name_lower:
                return True
        return category == '发票'
    
    def _resolve_name_conflict(self, target_path):
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
    
    def _generate_report(self):
        if not self.config.get('special_rules', {}).get('generate_report', True):
            return
        
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
            logger.info(f"报告已生成: {report_path}")
        except Exception as e:
            logger.error(f"生成报告失败: {str(e)}")


# ============== 图形界面 ==============
class MainWindow:
    def __init__(self):
        self.root = Tk()
        self.root.title("File Organizer Pro - 智能文件整理工具")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        self.target_dir = StringVar()
        self.mode = StringVar(value="auto")
        self.recursive = BooleanVar(value=False)
        self.preview = BooleanVar(value=False)
        
        self._setup_ui()
    
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        title_label = ttk.Label(main_frame, text="📁 File Organizer Pro", 
                                 font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=10)
        
        subtitle = ttk.Label(main_frame, text="智能文件整理工具 - 支持发票识别",
                             font=("微软雅黑", 10))
        subtitle.pack(pady=(0, 20))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=X, pady=10)
        
        dir_frame = ttk.LabelFrame(main_frame, text="📂 选择要整理的文件夹", padding="10")
        dir_frame.pack(fill=X, pady=10)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.target_dir, font=("Consolas", 10))
        dir_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(dir_frame, text="浏览...", command=self._browse_folder)
        browse_btn.pack(side=RIGHT)
        
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 整理选项", padding="10")
        options_frame.pack(fill=X, pady=10)
        
        ttk.Label(options_frame, text="分类模式:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        mode_combo = ttk.Combobox(options_frame, textvariable=self.mode, 
                                   values=["auto", "name", "extension"],
                                   state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive).grid(row=1, column=0, sticky=W, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="预览模式（不实际移动文件）", variable=self.preview).grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        start_btn = ttk.Button(btn_frame, text="🚀 开始整理", command=self._start_organize, width=20)
        start_btn.pack(side=LEFT, padx=10)
        
        clear_btn = ttk.Button(btn_frame, text="🗑️ 清空日志", command=self._clear_log, width=15)
        clear_btn.pack(side=LEFT, padx=10)
        
        log_frame = ttk.LabelFrame(main_frame, text="📋 运行日志", padding="10")
        log_frame.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=True)
        
        self.status_bar = ttk.Label(main_frame, text="就绪", relief=SUNKEN, anchor=W)
        self.status_bar.pack(fill=X, pady=(5, 0))
        
        self._log("File Organizer Pro 已启动")
        self._log("请选择一个文件夹开始整理")
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(title="请选择要整理的文件夹")
        if folder:
            self.target_dir.set(folder)
            self._log(f"已选择文件夹: {folder}")
    
    def _log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(END, f"[{timestamp}] {message}\n")
        self.log_text.see(END)
        self.root.update()
    
    def _clear_log(self):
        self.log_text.delete(1.0, END)
        self._log("日志已清空")
    
    def _start_organize(self):
        target_dir = self.target_dir.get().strip()
        
        if not target_dir:
            messagebox.showerror("错误", "请先选择要整理的文件夹！")
            return
        
        target_path = Path(target_dir)
        if not target_path.exists():
            messagebox.showerror("错误", f"文件夹不存在: {target_dir}")
            return
        
        if not self.preview.get():
            result = messagebox.askyesno("确认整理", f"即将整理文件夹:\n{target_dir}\n\n是否继续？")
            if not result:
                return
        
        self.status_bar.config(text="正在整理中...")
        thread = threading.Thread(target=self._run_organize, args=(target_path,))
        thread.daemon = True
        thread.start()
    
    def _run_organize(self, target_path):
        try:
            config_manager = ConfigManager()
            config = config_manager.load_config()
            
            organizer = FileOrganizer(
                target_dir=target_path,
                mode=self.mode.get(),
                recursive=self.recursive.get(),
                preview=self.preview.get(),
                config=config
            )
            
            self._log(f"开始整理: {target_path}")
            self._log(f"整理模式: {self.mode.get()}")
            
            result = organizer.run()
            
            self._log("=" * 50)
            self._log("整理完成！")
            self._log(f"总文件数: {result['total_files']}")
            self._log(f"已处理: {result['processed_files']}")
            self._log("\n分类统计:")
            for category, count in sorted(result['categories'].items()):
                self._log(f"  📂 {category}: {count} 个文件")
            
            self.root.after(0, lambda: messagebox.showinfo(
                "整理完成",
                f"整理完成！\n处理了 {result['processed_files']} 个文件"
            ))
            
        except Exception as e:
            self._log(f"❌ 整理失败: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("错误", f"整理失败:\n{str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.status_bar.config(text="就绪"))
    
    def run(self):
        self.root.mainloop()


# ============== 主函数 ==============
def resolve_path(path_str):
    path_str = path_str.strip().strip('"').strip("'")
    if path_str.startswith('~'):
        path_str = str(Path.home()) + path_str[1:]
    path = Path(path_str)
    if not path.is_absolute():
        path = Path.cwd() / path
    return path.resolve()


def main():
    parser = argparse.ArgumentParser(description="File Organizer Pro - 智能文件整理工具")
    parser.add_argument('-g', '--gui', action='store_true', help='启动图形界面')
    parser.add_argument('-d', '--directory', type=str, help='要整理的目录路径')
    parser.add_argument('-m', '--mode', choices=['name', 'extension', 'auto'],
                       default='auto', help='分类模式')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-p', '--preview', action='store_true', help='预览模式')
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("   File Organizer Pro - 智能文件整理工具")
    print("=" * 60 + "\n")
    
    if args.gui:
        print("正在启动图形界面...")
        app = MainWindow()
        app.run()
        return 0
    
    if not args.directory:
        print("❌ 错误: 请指定要整理的目录")
        print("\n使用方式: python file_organizer.py -d \"C:\\你的文件夹路径\"")
        print("或运行: python file_organizer.py --gui")
        return 1
    
    try:
        target_dir = resolve_path(args.directory)
    except Exception as e:
        print(f"❌ 路径解析失败: {str(e)}")
        return 1
    
    if not target_dir.exists():
        print(f"❌ 错误: 目录不存在 - {target_dir}")
        return 1
    
    print(f"📁 目标文件夹: {target_dir}")
    print(f"🔧 整理模式: {args.mode}")
    
    if not args.preview:
        confirm = input("是否继续整理？(y/n): ").lower()
        if confirm != 'y':
            print("已取消")
            return 0
    
    config_manager = ConfigManager()
    config = config_manager.load_config()
    
    organizer = FileOrganizer(
        target_dir=target_dir,
        mode=args.mode,
        recursive=args.recursive,
        preview=args.preview,
        config=config
    )
    
    try:
        result = organizer.run()
        print("\n✅ 整理完成!")
        print(f"📄 总文件数: {result['total_files']}")
        print(f"✅ 已处理: {result['processed_files']}")
        print("\n📊 分类统计:")
        for category, count in sorted(result['categories'].items()):
            print(f"   📂 {category}: {count} 个文件")
        return 0
    except Exception as e:
        print(f"\n❌ 整理失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

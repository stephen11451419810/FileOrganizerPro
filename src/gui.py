"""
图形界面模块 - 支持文件夹浏览器选择
"""

import sys
import os
import threading
from pathlib import Path
from tkinter import *
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.organizer import FileOrganizer
from src.utils import setup_logger


class MainWindow:
    """主窗口类"""
    
    def __init__(self):
        self.root = Tk()
        self.root.title("File Organizer Pro - 智能文件整理工具")
        self.root.geometry("850x650")
        self.root.resizable(True, True)
        
        self.target_dir = StringVar()
        self.mode = StringVar(value="auto")
        self.recursive = BooleanVar(value=False)
        self.preview = BooleanVar(value=False)
        self.ai_key = StringVar()
        
        self.logger = setup_logger()
        self._setup_ui()
    
    def _setup_ui(self):
        """设置界面"""
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="📁 File Organizer Pro", 
                                 font=("微软雅黑", 18, "bold"))
        title_label.pack(pady=10)
        
        subtitle = ttk.Label(main_frame, text="智能文件整理工具 - 支持发票识别和AI分类",
                             font=("微软雅黑", 10))
        subtitle.pack(pady=(0, 20))
        
        ttk.Separator(main_frame, orient='horizontal').pack(fill=X, pady=10)
        
        # 目标文件夹选择
        dir_frame = ttk.LabelFrame(main_frame, text="📂 选择要整理的文件夹", padding="10")
        dir_frame.pack(fill=X, pady=10)
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.target_dir, font=("Consolas", 10))
        dir_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(dir_frame, text="浏览...", command=self._browse_folder)
        browse_btn.pack(side=RIGHT)
        
        ttk.Label(dir_frame, text="💡 提示: 可以直接粘贴路径，或点击'浏览'选择",
                  font=("微软雅黑", 9), foreground="gray").pack(fill=X, pady=(5, 0))
        
        # 整理选项
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ 整理选项", padding="10")
        options_frame.pack(fill=X, pady=10)
        
        ttk.Label(options_frame, text="分类模式:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        mode_combo = ttk.Combobox(options_frame, textvariable=self.mode, 
                                   values=["auto", "name", "extension", "content", "ai"],
                                   state="readonly", width=15)
        mode_combo.grid(row=0, column=1, sticky=W, padx=5, pady=5)
        ttk.Label(options_frame, text="auto=智能组合 | name=按名称 | extension=按后缀 | content=按内容 | ai=AI识别",
                  font=("微软雅黑", 8), foreground="gray").grid(row=0, column=2, sticky=W, padx=10)
        
        ttk.Checkbutton(options_frame, text="递归处理子目录", variable=self.recursive).grid(row=1, column=0, sticky=W, padx=5, pady=5)
        ttk.Checkbutton(options_frame, text="预览模式（不实际移动文件）", variable=self.preview).grid(row=1, column=1, sticky=W, padx=5, pady=5)
        
        # AI设置
        ai_frame = ttk.LabelFrame(options_frame, text="🤖 AI 设置（可选）", padding="5")
        ai_frame.grid(row=2, column=0, columnspan=3, sticky=EW, padx=5, pady=10)
        
        ttk.Label(ai_frame, text="OpenAI API Key:").pack(side=LEFT, padx=5)
        ai_entry = ttk.Entry(ai_frame, textvariable=self.ai_key, width=50, show="*")
        ai_entry.pack(side=LEFT, fill=X, expand=True, padx=5)
        ttk.Label(ai_frame, text="(留空则使用其他模式)", font=("微软雅黑", 8), foreground="gray").pack(side=LEFT)
        
        # 按钮
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(pady=15)
        
        start_btn = ttk.Button(btn_frame, text="🚀 开始整理", command=self._start_organize, width=20)
        start_btn.pack(side=LEFT, padx=10)
        
        clear_btn = ttk.Button(btn_frame, text="🗑️ 清空日志", command=self._clear_log, width=15)
        clear_btn.pack(side=LEFT, padx=10)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="📋 运行日志", padding="10")
        log_frame.pack(fill=BOTH, expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=("Consolas", 9))
        self.log_text.pack(fill=BOTH, expand=True)
        
        # 状态栏
        self.status_bar = ttk.Label(main_frame, text="就绪", relief=SUNKEN, anchor=W)
        self.status_bar.pack(fill=X, pady=(5, 0))
        
        self._log("File Organizer Pro 已启动")
        self._log("请选择一个文件夹开始整理")
    
    def _browse_folder(self):
        folder = filedialog.askdirectory(title="请选择要整理的文件夹")
        if folder:
            self.target_dir.set(folder)
            self._log(f"已选择文件夹: {folder}")
    
    def _log(self, message: str):
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
    
    def _run_organize(self, target_path: Path):
        try:
            ai_key = self.ai_key.get().strip()
            if ai_key:
                os.environ['OPENAI_API_KEY'] = ai_key
            
            organizer = FileOrganizer(
                target_dir=target_path,
                mode=self.mode.get(),
                recursive=self.recursive.get(),
                preview=self.preview.get(),
                config={}
            )
            
            self._log(f"开始整理: {target_path}")
            self._log(f"整理模式: {self.mode.get()}")
            
            result = organizer.run()
            
            self._log("=" * 50)
            self._log("整理完成！")
            self._log(f"总文件数: {result['total_files']}")
            self._log(f"已处理: {result['processed_files']}")
            self._log(f"耗时: {result.get('elapsed_seconds', 0):.2f} 秒")
            self._log("\n分类统计:")
            for category, count in sorted(result['categories'].items()):
                self._log(f"  📂 {category}: {count} 个文件")
            
            if result.get('report_path'):
                self._log(f"\n📄 详细报告: {result['report_path']}")
            
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

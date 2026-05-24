#!/usr/bin/env python3
"""
文件整理工具 - 主入口
支持多种路径输入方式
"""

import sys
import os
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.organizer import FileOrganizer
from src.utils import setup_logger, ConfigManager


def resolve_path(path_str: str) -> Path:
    """解析用户输入的路径，支持绝对路径、相对路径、拖拽、用户目录"""
    path_str = path_str.strip().strip('"').strip("'")
    
    if path_str.startswith('~'):
        path_str = str(Path.home()) + path_str[1:]
    
    path = Path(path_str)
    
    if not path.is_absolute():
        path = Path.cwd() / path
    
    return path.resolve()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="File Organizer Pro - 智能文件整理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python main.py --gui                           # 启动图形界面
  python main.py -d "C:\\Users\\用户名\\Downloads" -m auto
  python main.py -d "./Downloads" -m auto
  python main.py -d "~/Desktop" -m auto
  python main.py -d "文件夹路径" --preview
        """
    )
    
    parser.add_argument('-g', '--gui', action='store_true', 
                       help='启动图形界面模式')
    parser.add_argument('-d', '--directory', type=str, 
                       help='要整理的目录路径')
    parser.add_argument('-m', '--mode', choices=['name', 'extension', 'content', 'ai', 'auto'],
                       default='auto', help='分类模式')
    parser.add_argument('-r', '--recursive', action='store_true',
                       help='递归处理子目录')
    parser.add_argument('-p', '--preview', action='store_true',
                       help='预览模式')
    parser.add_argument('--ai-key', type=str,
                       help='OpenAI API Key')
    parser.add_argument('--config', type=str,
                       help='配置文件路径')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    logger = setup_logger()
    print("\n" + "=" * 60)
    print("   File Organizer Pro - 智能文件整理工具")
    print("=" * 60 + "\n")
    
    if args.gui:
        print("正在启动图形界面...")
        from src.gui import MainWindow
        app = MainWindow()
        app.run()
        return 0
    
    if not args.directory:
        print("❌ 错误: 请指定要整理的目录")
        print("\n使用方式:")
        print("   python main.py -d \"C:\\你的文件夹路径\"")
        print("   python main.py --gui")
        print("\n或者直接运行: run.bat")
        return 1
    
    try:
        target_dir = resolve_path(args.directory)
    except Exception as e:
        print(f"❌ 路径解析失败: {str(e)}")
        return 1
    
    if not target_dir.exists():
        print(f"❌ 错误: 目录不存在 - {target_dir}")
        return 1
    
    if not target_dir.is_dir():
        print(f"❌ 错误: 路径不是文件夹 - {target_dir}")
        return 1
    
    print(f"📁 目标文件夹: {target_dir}")
    print(f"🔧 整理模式: {args.mode}")
    print(f"📂 递归处理: {'是' if args.recursive else '否'}")
    print(f"👁️ 预览模式: {'是' if args.preview else '否'}\n")
    
    if not args.preview:
        confirm = input("是否继续整理？(y/n): ").lower()
        if confirm != 'y':
            print("已取消")
            return 0
    
    if args.ai_key:
        os.environ['OPENAI_API_KEY'] = args.ai_key
    
    config_manager = ConfigManager(args.config)
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
        
        print("\n" + "=" * 50)
        print("✅ 整理完成!")
        print("=" * 50)
        print(f"📁 目标目录: {result['target_dir']}")
        print(f"📄 总文件数: {result['total_files']}")
        print(f"✅ 已处理: {result['processed_files']}")
        print(f"❌ 错误: {len(result['errors'])}")
        print(f"⏱️ 耗时: {result.get('elapsed_seconds', 0):.2f} 秒")
        
        print("\n📊 分类统计:")
        for category, count in sorted(result['categories'].items()):
            bar = "█" * min(count, 20) + "░" * (20 - min(count, 20))
            print(f"   📂 {category:10} : {count:4} 个 {bar}")
        
        if result.get('report_path'):
            print(f"\n📄 详细报告: {result['report_path']}")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断操作")
        return 1
    except Exception as e:
        logger.error(f"整理失败: {str(e)}")
        print(f"\n❌ 整理失败: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

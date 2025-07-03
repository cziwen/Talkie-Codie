#!/usr/bin/env python3
"""
缓存清理脚本
清理 cache 文件夹中的所有生成文件
"""

import os
import shutil
import sys

def clear_cache(cache_dir="cache", confirm=True):
    """
    清理缓存文件夹
    
    Args:
        cache_dir: 缓存目录路径
        confirm: 是否确认删除
    """
    if not os.path.exists(cache_dir):
        print(f"缓存目录不存在: {cache_dir}")
        return
    
    # 统计文件数量
    total_files = 0
    file_types = {}
    
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            total_files += 1
            ext = os.path.splitext(file)[1]
            file_types[ext] = file_types.get(ext, 0) + 1
    
    if total_files == 0:
        print("缓存目录为空，无需清理")
        return
    
    print(f"发现 {total_files} 个文件:")
    for ext, count in file_types.items():
        print(f"  {ext}: {count} 个文件")
    
    if confirm:
        response = input(f"\n确定要删除 cache 目录中的所有文件吗？(y/n): ").lower().strip()
        if response not in ['y', 'yes', '是']:
            print("操作已取消")
            return
    
    try:
        # 删除缓存目录中的所有内容
        for root, dirs, files in os.walk(cache_dir, topdown=False):
            for file in files:
                file_path = os.path.join(root, file)
                os.remove(file_path)
                print(f"已删除: {file_path}")
            
            # 删除空目录（除了根目录）
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                if os.path.exists(dir_path) and not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    print(f"已删除空目录: {dir_path}")
        
        print(f"\n✅ 缓存清理完成！共删除 {total_files} 个文件")
        
    except Exception as e:
        print(f"❌ 清理过程中出现错误: {e}")

def show_cache_info(cache_dir="cache"):
    """显示缓存信息"""
    if not os.path.exists(cache_dir):
        print(f"缓存目录不存在: {cache_dir}")
        return
    
    print(f"=== 缓存目录信息: {cache_dir} ===")
    
    total_size = 0
    file_types = {}
    
    for root, dirs, files in os.walk(cache_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size
                ext = os.path.splitext(file)[1]
                file_types[ext] = file_types.get(ext, 0) + 1
            except OSError:
                pass
    
    print(f"总文件数: {sum(file_types.values())}")
    print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
    print("\n文件类型分布:")
    for ext, count in file_types.items():
        print(f"  {ext}: {count} 个文件")

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "info":
            show_cache_info()
        elif command == "clear":
            clear_cache(confirm=True)
        elif command == "clear-force":
            clear_cache(confirm=False)
        else:
            print("用法:")
            print("  python scripts/clear_cache.py info      # 显示缓存信息")
            print("  python scripts/clear_cache.py clear     # 清理缓存（需要确认）")
            print("  python scripts/clear_cache.py clear-force # 强制清理缓存")
    else:
        print("=== 缓存管理工具 ===")
        print("1. 显示缓存信息")
        print("2. 清理缓存")
        print("3. 退出")
        
        choice = input("\n请选择操作 (1-3): ").strip()
        
        if choice == "1":
            show_cache_info()
        elif choice == "2":
            clear_cache()
        elif choice == "3":
            print("退出")
        else:
            print("无效选择")

if __name__ == "__main__":
    main() 
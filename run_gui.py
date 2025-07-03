#!/usr/bin/env python3
"""
Talkie-Codie GUI 启动脚本
自动检查依赖并启动 GUI 界面
"""

import sys
import subprocess
import importlib.util


def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    required_packages = [
        'PyQt6',
        'sounddevice',
        'scipy',
        'numpy',
        'faster-whisper',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if package == 'PyQt6':
            spec = importlib.util.find_spec('PyQt6')
        else:
            spec = importlib.util.find_spec(package)
        
        if spec is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("检测到缺少以下依赖包:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\n正在安装依赖包...")
        try:
            for package in missing_packages:
                install_package = package
                
                print(f"安装 {install_package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', install_package
                ])
            
            print("依赖安装完成！")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"安装依赖失败: {e}")
            print("请手动运行: pip install -r requirements.txt")
            return False
    else:
        print("所有依赖已安装")
        return True


def main():
    """主函数"""
    print("=== Talkie-Codie GUI 启动器 ===")
    print("检查依赖...")
    
    if not check_and_install_dependencies():
        return 1
    
    print("\n启动 GUI 界面...")
    try:
        # 导入并运行 GUI
        from src.main_gui import NewMainWindow
        import sys
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = NewMainWindow()
        window.show()
        return app.exec()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保项目结构正确")
        return 1
    except Exception as e:
        print(f"启动失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
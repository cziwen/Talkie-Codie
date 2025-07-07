#!/usr/bin/env python3
"""
Talkie-Codie GUI 启动脚本
自动检查依赖并启动 GUI 界面
"""

import sys
import subprocess
import importlib.util


def check_and_install_dependencies():
    """Check and install necessary dependencies"""
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
        print("Detected missing dependencies:")
        for package in missing_packages:
            print(f"  - {package}")
        
        print("\nInstalling dependencies...")
        try:
            for package in missing_packages:
                install_package = package
                
                print(f"Installing {install_package}...")
                subprocess.check_call([
                    sys.executable, '-m', 'pip', 'install', install_package
                ])
            
            print("Dependencies installation completed!")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            print("Please run manually: pip install -r requirements.txt")
            return False
    else:
        print("All dependencies are installed")
        return True


def main():
    """Main function"""
    print("=== Talkie-Codie GUI Launcher ===")
    print("Checking dependencies...")
    
    if not check_and_install_dependencies():
        return 1
    
    print("\nStarting GUI interface...")
    try:
        # Import and run GUI
        from src.main_gui import NewMainWindow
        import sys
        from PyQt6.QtWidgets import QApplication
        
        app = QApplication(sys.argv)
        window = NewMainWindow()
        window.show()
        return app.exec()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please ensure project structure is correct")
        return 1
    except Exception as e:
        print(f"Startup failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
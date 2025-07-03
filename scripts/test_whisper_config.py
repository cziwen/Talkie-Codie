#!/usr/bin/env python3
"""
测试Whisper配置是否正常工作
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_whisper_config():
    """测试whisper配置加载"""
    try:
        from audio.whisper_transcriber import load_whisper_config
        
        print("=== 测试Whisper配置加载 ===")
        config = load_whisper_config()
        
        print("配置加载成功！")
        print(f"设备类型: {config['device']}")
        print(f"计算类型: {config['compute_type']}")
        print(f"模型大小: {config['model_size']}")
        print(f"Beam size: {config['beam_size']}")
        print(f"语言: {config['language'] or '自动检测'}")
        print(f"VAD过滤: {'启用' if config['vad_filter'] else '禁用'}")
        
        return True
        
    except Exception as e:
        print(f"配置加载失败: {e}")
        return False

def test_whisper_import():
    """测试whisper模块导入"""
    try:
        print("\n=== 测试Whisper模块导入 ===")
        
        # 测试faster-whisper导入
        try:
            import faster_whisper
            print("✓ faster-whisper 导入成功")
        except ImportError:
            print("✗ faster-whisper 未安装，请运行: pip install faster-whisper")
            return False
        
        # 测试torch导入（用于CUDA检测）
        try:
            import torch
            print("✓ PyTorch 导入成功")
            if torch.cuda.is_available():
                print("✓ CUDA 可用")
            else:
                print("⚠ CUDA 不可用，将使用CPU")
        except ImportError:
            print("⚠ PyTorch 未安装，无法检测CUDA")
        
        return True
        
    except Exception as e:
        print(f"模块导入测试失败: {e}")
        return False

def main():
    print("=== Whisper配置测试工具 ===")
    
    # 测试模块导入
    if not test_whisper_import():
        print("\n请先安装必要的依赖包")
        return
    
    # 测试配置加载
    if not test_whisper_config():
        print("\n配置测试失败")
        return
    
    print("\n=== 测试完成 ===")
    print("所有测试通过！Whisper配置正常工作。")
    print("\n提示:")
    print("- 要修改配置，请运行: python scripts/configure_whisper.py")
    print("- 要使用CUDA加速，请确保安装了支持CUDA的PyTorch版本")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Whisper配置管理工具
用于设置whisper的设备类型、计算类型等参数
"""

import json
import os
import sys

def load_config():
    """加载当前配置"""
    config_path = os.path.join("config", "whisper_config.json")
    default_config = {
        "device": "cpu",
        "compute_type": "int8",
        "model_size": "base",
        "beam_size": 5,
        "language": None,
        "task": "transcribe",
        "vad_filter": True,
        "vad_parameters": {
            "min_silence_duration_ms": 500
        }
    }
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 合并默认配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return default_config
    else:
        return default_config

def save_config(config):
    """保存配置到文件"""
    config_path = os.path.join("config", "whisper_config.json")
    os.makedirs("config", exist_ok=True)
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        print(f"配置已保存到: {config_path}")
        return True
    except Exception as e:
        print(f"保存配置文件失败: {e}")
        return False

def check_cuda_availability():
    """检查CUDA是否可用"""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False

def configure_device(config):
    """配置设备类型"""
    print("\n=== 设备配置 ===")
    print(f"当前设备: {config['device']}")
    
    cuda_available = check_cuda_availability()
    if cuda_available:
        print("✓ CUDA可用")
        print("1. CPU (推荐用于低配置设备)")
        print("2. CUDA (推荐用于有GPU的设备)")
    else:
        print("✗ CUDA不可用")
        print("1. CPU (唯一可用选项)")
    
    while True:
        choice = input("请选择设备类型 (1-2): ").strip()
        if choice == "1":
            config["device"] = "cpu"
            break
        elif choice == "2" and cuda_available:
            config["device"] = "cuda"
            break
        else:
            print("无效选择，请重试")

def configure_compute_type(config):
    """配置计算类型"""
    print("\n=== 计算类型配置 ===")
    print(f"当前计算类型: {config['compute_type']}")
    
    compute_types = {
        "1": ("int8", "最快，内存占用最少，精度较低"),
        "2": ("int16", "平衡速度和精度"),
        "3": ("float16", "较高精度，需要更多内存"),
        "4": ("float32", "最高精度，需要最多内存")
    }
    
    print("可用的计算类型:")
    for key, (ctype, desc) in compute_types.items():
        print(f"{key}. {ctype} - {desc}")
    
    while True:
        choice = input("请选择计算类型 (1-4): ").strip()
        if choice in compute_types:
            config["compute_type"] = compute_types[choice][0]
            break
        else:
            print("无效选择，请重试")

def configure_model_size(config):
    """配置模型大小"""
    print("\n=== 模型大小配置 ===")
    print(f"当前模型大小: {config['model_size']}")
    
    model_sizes = {
        "1": ("tiny", "最快，准确度较低，约39MB"),
        "2": ("base", "平衡速度和准确度，约74MB"),
        "3": ("small", "更准确，稍慢，约244MB"),
        "4": ("medium", "高准确度，较慢，约769MB"),
        "5": ("large", "最高准确度，最慢，约1550MB")
    }
    
    print("可用的模型大小:")
    for key, (size, desc) in model_sizes.items():
        print(f"{key}. {size} - {desc}")
    
    while True:
        choice = input("请选择模型大小 (1-5): ").strip()
        if choice in model_sizes:
            config["model_size"] = model_sizes[choice][0]
            break
        else:
            print("无效选择，请重试")

def configure_advanced_options(config):
    """配置高级选项"""
    print("\n=== 高级选项配置 ===")
    
    # Beam size配置
    print(f"当前beam size: {config['beam_size']}")
    beam_size = input("请输入beam size (1-10，默认5): ").strip()
    if beam_size:
        try:
            config["beam_size"] = int(beam_size)
        except ValueError:
            print("无效的beam size，保持默认值")
    
    # 语言配置
    print(f"当前语言设置: {config['language'] or '自动检测'}")
    language = input("请输入语言代码 (如zh, en，留空为自动检测): ").strip()
    if language:
        config["language"] = language
    else:
        config["language"] = None
    
    # VAD过滤配置
    print(f"当前VAD过滤: {'启用' if config['vad_filter'] else '禁用'}")
    vad_choice = input("是否启用VAD过滤 (y/n，默认y): ").strip().lower()
    if vad_choice in ['n', 'no']:
        config["vad_filter"] = False
    else:
        config["vad_filter"] = True

def show_current_config(config):
    """显示当前配置"""
    print("\n=== 当前配置 ===")
    print(f"设备类型: {config['device']}")
    print(f"计算类型: {config['compute_type']}")
    print(f"模型大小: {config['model_size']}")
    print(f"Beam size: {config['beam_size']}")
    print(f"语言: {config['language'] or '自动检测'}")
    print(f"VAD过滤: {'启用' if config['vad_filter'] else '禁用'}")
    print(f"任务类型: {config['task']}")

def main():
    print("=== Whisper配置管理工具 ===")
    
    # 加载当前配置
    config = load_config()
    
    while True:
        print("\n请选择操作:")
        print("1. 查看当前配置")
        print("2. 配置设备类型 (CPU/CUDA)")
        print("3. 配置计算类型")
        print("4. 配置模型大小")
        print("5. 配置高级选项")
        print("6. 保存配置")
        print("0. 退出")
        
        choice = input("\n请输入选择 (0-6): ").strip()
        
        if choice == "0":
            print("退出配置工具")
            break
        elif choice == "1":
            show_current_config(config)
        elif choice == "2":
            configure_device(config)
        elif choice == "3":
            configure_compute_type(config)
        elif choice == "4":
            configure_model_size(config)
        elif choice == "5":
            configure_advanced_options(config)
        elif choice == "6":
            if save_config(config):
                print("配置保存成功！")
            break
        else:
            print("无效选择，请重试")

if __name__ == "__main__":
    main() 
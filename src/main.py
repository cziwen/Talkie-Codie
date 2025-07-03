#!/usr/bin/env python3
"""
Talkie-Codie 主程序
语音转文本的完整流程，包含 LLM 优化
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio.core import AudioProcessor
from src.llm.manager import LLMManager

def main():
    """主程序入口"""
    print("=== Talkie-Codie 语音转文本工具 ===")
    print("将您的语音转换为文本，并使用 LLM 优化为更好的 prompt\n")
    
    # 初始化音频处理器
    processor = AudioProcessor()
    
    # 初始化 LLM 管理器
    llm_manager = LLMManager()
    
    # 检查 LLM 配置
    if not llm_manager.current_provider:
        print("LLM 提供商未配置，将跳过 prompt 优化步骤")
        print("请配置 config/llm_config.json 文件")
        use_llm = False
    else:
        print(f"当前 LLM 提供商: {llm_manager.get_current_provider_info()}")
        use_llm = True
    
    # 列出音频设备
    devices = processor.list_audio_devices()
    print()
    
    # 选择音频设备
    device_idx = input("请输入你想使用的输入设备编号（默认回车为系统默认）: ")
    device = None
    if device_idx.strip():
        try:
            device = int(device_idx)
            if device < 0 or device >= len(devices):
                print("设备编号超出范围，使用默认设备。")
                device = None
        except ValueError:
            print("输入无效，使用默认设备。")
            device = None
    
    # 检查音频输入
    if not processor.check_audio_levels(2, device=device):
        print("请检查麦克风连接和系统权限设置")
        return
    
    # 设置录音参数
    duration = input("请输入录音时长（秒，默认5）：")
    try:
        duration = float(duration)
    except ValueError:
        duration = 5
    duration = int(duration)
    
    # 选择 Whisper 模型
    print("\n可用的 Whisper 模型大小:")
    print("tiny: 最快，准确度较低")
    print("base: 平衡速度和准确度 (推荐)")
    print("small: 更准确，稍慢")
    print("medium: 高准确度，较慢")
    print("large: 最高准确度，最慢")
    
    model_size = input("请选择模型大小 (默认 base): ").strip() or "base"
    
    # 询问是否使用自定义文件名
    use_custom_name = input("是否使用自定义文件名？(y/n，默认n): ").lower().strip() in ['y', 'yes', '是']
    output_path = None
    if use_custom_name:
        custom_name = input("请输入自定义文件名（不含扩展名）：").strip()
        if custom_name:
            output_path = f"cache/audio/{custom_name}.wav"
    
    try:
        # 执行完整的录音并转录流程
        transcript, audio_path, transcript_path = processor.record_and_transcribe(
            duration=duration,
            model_size=model_size,
            device=device,
            output_path=output_path
        )
        
        print(f"\n=== 转录结果 ===")
        print(transcript)
        
        # LLM 优化
        if use_llm:
            print(f"\n=== LLM 优化 ===")
            
            # 选择任务类型
            print("请选择任务类型:")
            print("1. general - 通用优化")
            print("2. coding - 编程相关")
            print("3. writing - 写作相关")
            print("4. analysis - 分析相关")
            
            task_choice = input("请选择任务类型 (1-4，默认1): ").strip() or "1"
            task_types = {"1": "general", "2": "coding", "3": "writing", "4": "analysis"}
            task_type = task_types.get(task_choice, "general")
            
            print(f"使用任务类型: {task_type}")
            
            # 选择优化档位
            print("\n请选择优化档位:")
            print("1. default - 简洁优化")
            print("2. pro - 专业优化")
            
            level_choice = input("请选择档位 (1-2，默认1): ").strip() or "1"
            levels = {"1": "default", "2": "pro"}
            level = levels.get(level_choice, "default")
            
            print(f"使用档位: {level}")
            print("正在优化 prompt...")
            
            result = llm_manager.optimize_prompt(transcript, task_type, level)
            
            # 处理返回结果
            if isinstance(result, tuple):
                optimized_prompt, optimized_path = result
            else:
                optimized_prompt = result
                optimized_path = None
            
            print(f"\n=== 优化后的 Prompt ===")
            print(optimized_prompt)
        
        print(f"\n=== 流程完成 ===")
        print("音频文件:", audio_path)
        if transcript_path:
            print("转录文件:", transcript_path)
        if use_llm and optimized_path:
            print("优化文件:", optimized_path)
        
        # 询问是否继续
        while True:
            choice = input("\n是否继续录音转录？(y/n): ").lower().strip()
            if choice in ['y', 'yes', '是']:
                print("\n" + "="*50 + "\n")
                main()  # 递归调用，重新开始
                break
            elif choice in ['n', 'no', '否']:
                print("感谢使用 Talkie-Codie！")
                break
            else:
                print("请输入 y 或 n")
        
    except Exception as e:
        print(f"程序执行过程中出现错误: {e}")
        print("请检查音频文件是否存在，或重新运行程序。")

if __name__ == "__main__":
    main() 
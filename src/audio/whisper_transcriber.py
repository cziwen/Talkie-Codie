from faster_whisper import WhisperModel
import os
import json

def load_whisper_config():
    """
    加载whisper配置文件
    
    Returns:
        dict: 配置字典
    """
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
                # 合并默认配置和用户配置
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"读取配置文件失败: {e}，使用默认配置")
            return default_config
    else:
        print("配置文件不存在，使用默认配置")
        return default_config

def transcribe_audio(audio_path, model_size=None):
    """
    使用 faster-whisper 转录音频文件
    
    Args:
        audio_path (str): 音频文件路径
        model_size (str): 模型大小 ("tiny", "base", "small", "medium", "large")
    
    Returns:
        tuple: (转录的文本, 检测到的语言)
    """
    # 加载配置
    config = load_whisper_config()
    
    # 如果传入了model_size参数，则覆盖配置文件中的设置
    if model_size:
        config["model_size"] = model_size
    
    print(f"正在加载 Whisper 模型: {config['model_size']}")
    print(f"使用设备: {config['device']}")
    print(f"计算类型: {config['compute_type']}")
    
    # 加载模型 (首次运行会下载模型)
    model = WhisperModel(
        config["model_size"], 
        device=config["device"], 
        compute_type=config["compute_type"]
    )
    
    print(f"开始转录音频文件: {audio_path}")
    
    # 准备转录参数
    transcribe_kwargs = {
        "beam_size": config["beam_size"],
        "task": config["task"]
    }
    
    # 如果指定了语言，添加到参数中
    if config["language"]:
        transcribe_kwargs["language"] = config["language"]
    
    # 如果启用了VAD过滤，添加到参数中
    if config["vad_filter"]:
        transcribe_kwargs["vad_filter"] = True
        transcribe_kwargs["vad_parameters"] = config["vad_parameters"]
    
    # 转录音频
    segments, info = model.transcribe(audio_path, **transcribe_kwargs)
    
    # 收集转录结果
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    
    print(f"转录完成！")
    print(f"检测到的语言: {info.language} (置信度: {info.language_probability:.2f})")
    
    return transcript.strip(), info.language

def main():
    print("=== Talkie-Codie 语音转录工具 ===")
    
    # 检查是否有录音文件
    if os.path.exists("output.wav"):
        audio_path = "output.wav"
        print(f"找到录音文件: {audio_path}")
    else:
        audio_path = input("请输入音频文件路径: ")
        if not os.path.exists(audio_path):
            print("文件不存在！")
            return
    
    # 选择模型大小
    print("\n可用的模型大小:")
    print("tiny: 最快，准确度较低")
    print("base: 平衡速度和准确度 (推荐)")
    print("small: 更准确，稍慢")
    print("medium: 高准确度，较慢")
    print("large: 最高准确度，最慢")
    
    model_size = input("请选择模型大小 (默认 base): ").strip() or "base"
    
    # 转录
    try:
        transcript, detected_language = transcribe_audio(audio_path, model_size)
        print(f"\n转录结果:\n{transcript}")
        print(f"检测到的语言: {detected_language}")
        
        # 保存转录结果
        output_file = audio_path.replace(".wav", "_transcript.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"\n转录结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"转录过程中出现错误: {e}")

if __name__ == "__main__":
    main() 
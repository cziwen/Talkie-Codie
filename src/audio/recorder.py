import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

SAMPLE_RATE = 16000  # 采样率
CHANNELS = 1         # 单声道


def list_audio_devices():
    """列出可用的音频设备，带编号"""
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        print(f"{idx}: {dev['name']} (输入通道: {dev['max_input_channels']}, 输出通道: {dev['max_output_channels']})")
    return devices


def check_audio_levels(duration=3, device=None):
    """检查音频输入电平"""
    print(f"检查音频输入电平 {duration} 秒...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=device)
    sd.wait()
    
    # 计算音量
    volume = np.sqrt(np.mean(audio**2))
    print(f"检测到的音量级别: {volume}")
    
    if volume < 30:  # 阈值可调整
        print("警告: 音量过低，可能没有检测到声音输入")
        return False
    return True


def record_audio(duration=5, output_path="output.wav", device=None):
    print(f"开始录音，时长 {duration} 秒...")
    print("请开始说话...")
    
    # 录音
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=device)
    sd.wait()  # 等待录音结束
    
    # 检查录音质量
    volume = np.sqrt(np.mean(audio**2))
    print(f"录音完成，音量级别: {volume}")
    
    if volume < 20:
        print("警告: 录音音量过低，请检查麦克风设置")
    
    # 保存文件
    write(output_path, SAMPLE_RATE, audio)
    print(f"录音已保存到 {output_path}")
    
    return audio


def main():
    print("=== Talkie-Codie 录音工具 ===")
    
    # 列出音频设备
    devices = list_audio_devices()
    print()
    
    # 检查音频输入
    device_idx = input("请输入你想使用的输入设备编号（默认回车为系统默认）: ")
    if device_idx.strip() == "":
        device = None
    else:
        try:
            device = int(device_idx)
            if device < 0 or device >= len(devices):
                print("设备编号超出范围，使用默认设备。")
                device = None
        except ValueError:
            print("输入无效，使用默认设备。")
            device = None
    
    if not check_audio_levels(2, device=device):
        print("请检查麦克风连接和系统权限设置")
        return
    
    duration = input("请输入录音时长（秒，默认5）：")
    try:
        duration = float(duration)
    except ValueError:
        duration = 5
    duration = int(duration)  # 修复类型错误
    
    output_path = input("请输入保存文件名（默认 output.wav）：") or "output.wav"
    
    record_audio(duration, output_path, device=device)


if __name__ == "__main__":
    main() 
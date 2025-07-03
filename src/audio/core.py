import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import time
from datetime import datetime
from faster_whisper import WhisperModel

class AudioProcessor:
    """音频处理核心类，整合录音和转录功能"""
    
    def __init__(self, sample_rate=16000, channels=1, cache_dir="cache"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.whisper_model = None
        self.cache_dir = cache_dir
        
        # 确保缓存目录存在
        self._ensure_cache_dirs()
    
    def _ensure_cache_dirs(self):
        """确保缓存目录存在"""
        dirs = [
            os.path.join(self.cache_dir, "audio"),
            os.path.join(self.cache_dir, "transcripts"),
            os.path.join(self.cache_dir, "optimized")
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _generate_filename(self, prefix="", extension=".wav"):
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if prefix:
            return f"{prefix}_{timestamp}{extension}"
        return f"{timestamp}{extension}"
        
    def list_audio_devices(self):
        """列出可用的音频设备"""
        devices = sd.query_devices()
        print("可用的音频设备:")
        for idx, dev in enumerate(devices):
            print(f"{idx}: {dev['name']} (输入通道: {dev['max_input_channels']}, 输出通道: {dev['max_output_channels']})")
        return devices
    
    def check_audio_levels(self, duration=3, device=None):
        """检查音频输入电平"""
        print(f"检查音频输入电平 {duration} 秒...")
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
                      channels=self.channels, dtype='int16', device=device)
        sd.wait()
        
        volume = np.sqrt(np.mean(audio**2))
        print(f"检测到的音量级别: {volume}")
        
        if volume < 30:
            print("警告: 音量过低，可能没有检测到声音输入")
            return False
        return True
    
    def record_audio(self, duration=5, output_path=None, device=None):
        """录制音频"""
        # 如果没有指定输出路径，使用缓存目录
        if output_path is None:
            audio_filename = self._generate_filename("audio", ".wav")
            output_path = os.path.join(self.cache_dir, "audio", audio_filename)
        
        print(f"开始录音，时长 {duration} 秒...")
        print("请开始说话...")
        
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
                      channels=self.channels, dtype='int16', device=device)
        sd.wait()
        
        volume = np.sqrt(np.mean(audio**2))
        print(f"录音完成，音量级别: {volume}")
        
        if volume < 20:
            print("警告: 录音音量过低，请检查麦克风设置")
        
        write(output_path, self.sample_rate, audio)
        print(f"录音已保存到 {output_path}")
        
        return audio, output_path
    
    def load_whisper_model(self, model_size="base"):
        """加载 Whisper 模型"""
        if self.whisper_model is None or self.whisper_model.model_size != model_size:
            print(f"正在加载 Whisper 模型: {model_size}")
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        return self.whisper_model
    
    def transcribe_audio(self, audio_path, model_size="base", save_transcript=True):
        """转录音频文件"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        model = self.load_whisper_model(model_size)
        print(f"开始转录音频文件: {audio_path}")
        
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "
        
        transcript = transcript.strip()
        
        print(f"转录完成！")
        print(f"检测到的语言: {info.language} (置信度: {info.language_probability:.2f})")
        
        # 保存转录结果到缓存目录
        if save_transcript:
            transcript_filename = self._generate_filename("transcript", ".txt")
            transcript_path = os.path.join(self.cache_dir, "transcripts", transcript_filename)
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"转录结果已保存到: {transcript_path}")
            return transcript, transcript_path
        
        return transcript
    
    def record_and_transcribe(self, duration=5, model_size="base", device=None, 
                            output_path=None, save_transcript=True):
        """完整的录音并转录流程"""
        print("=== 开始录音并转录流程 ===")
        
        # 1. 录音
        audio, audio_path = self.record_audio(duration, output_path, device)
        
        # 2. 转录
        if save_transcript:
            transcript, transcript_path = self.transcribe_audio(audio_path, model_size, save_transcript=True)
        else:
            transcript = self.transcribe_audio(audio_path, model_size, save_transcript=False)
            transcript_path = None
        
        return transcript, audio_path, transcript_path 
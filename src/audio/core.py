import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os
import time
from datetime import datetime
from faster_whisper import WhisperModel

class AudioProcessor:
    """Audio processing core class, integrating recording and transcription functionality"""
    
    def __init__(self, sample_rate=16000, channels=1, cache_dir="cache"):
        self.sample_rate = sample_rate
        self.channels = channels
        self.whisper_model = None
        self.cache_dir = cache_dir
        
        # Ensure cache directory exists
        self._ensure_cache_dirs()
    
    def _ensure_cache_dirs(self):
        """Ensure cache directories exist"""
        dirs = [
            os.path.join(self.cache_dir, "audio"),
            os.path.join(self.cache_dir, "transcripts"),
            os.path.join(self.cache_dir, "optimized")
        ]
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
    
    def _generate_filename(self, prefix="", extension=".wav"):
        """Generate filename with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if prefix:
            return f"{prefix}_{timestamp}{extension}"
        return f"{timestamp}{extension}"
        
    def list_audio_devices(self):
        """List available audio devices"""
        devices = sd.query_devices()
        print("Available audio devices:")
        for idx, dev in enumerate(devices):
            name = dev.get('name', f'Device{idx}')
            max_input = dev.get('max_input_channels', 0)
            max_output = dev.get('max_output_channels', 0)
            print(f"{idx}: {name} (Input channels: {max_input}, Output channels: {max_output})")
        return devices
    
    def check_audio_levels(self, duration=3, device=None):
        """Check audio input levels"""
        print(f"Checking audio input levels for {duration} seconds...")
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
                      channels=self.channels, dtype='int16', device=device)
        sd.wait()
        
        volume = np.sqrt(np.mean(audio**2))
        print(f"Detected volume level: {volume}")
        
        if volume < 30:
            print("Warning: Volume too low, may not detect audio input")
            return False
        return True
    
    def record_audio(self, duration=5, output_path=None, device=None):
        """Record audio"""
        # If no output path specified, use cache directory
        if output_path is None:
            audio_filename = self._generate_filename("audio", ".wav")
            output_path = os.path.join(self.cache_dir, "audio", audio_filename)
        
        print(f"Starting recording for {duration} seconds...")
        print("Please start speaking...")
        
        audio = sd.rec(int(duration * self.sample_rate), samplerate=self.sample_rate, 
                      channels=self.channels, dtype='int16', device=device)
        sd.wait()
        
        volume = np.sqrt(np.mean(audio**2))
        print(f"Recording completed, volume level: {volume}")
        
        if volume < 20:
            print("Warning: Recording volume too low, please check microphone settings")
        
        write(output_path, self.sample_rate, audio)
        print(f"Recording saved to {output_path}")
        
        return audio, output_path, volume
    
    def load_whisper_model(self, model_size="base"):
        """Load Whisper model"""
        # For compatibility, always reload model to avoid accessing unknown attributes
        print(f"Loading Whisper model: {model_size}")
        self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
        return self.whisper_model
    
    def transcribe_audio(self, audio_path, model_size="base", save_transcript=True):
        """Transcribe audio file"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        model = self.load_whisper_model(model_size)
        print(f"Starting transcription of audio file: {audio_path}")
        
        segments, info = model.transcribe(audio_path, beam_size=5)
        
        transcript = ""
        for segment in segments:
            transcript += segment.text + " "
        
        transcript = transcript.strip()
        
        print(f"Transcription completed!")
        print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
        
        # Save transcription result to cache directory
        if save_transcript:
            transcript_filename = self._generate_filename("transcript", ".txt")
            transcript_path = os.path.join(self.cache_dir, "transcripts", transcript_filename)
            with open(transcript_path, "w", encoding="utf-8") as f:
                f.write(transcript)
            print(f"Transcription result saved to: {transcript_path}")
            return transcript, transcript_path, info.language
        
        return transcript, None, info.language
    
    def record_and_transcribe(self, duration=5, model_size="base", device=None, 
                            output_path=None, save_transcript=True):
        """Complete recording and transcription workflow"""
        print("=== Starting recording and transcription workflow ===")
        
        # 1. Record audio
        audio, audio_path, volume = self.record_audio(duration, output_path, device)
        
        # 2. Transcribe
        if save_transcript:
            transcript, transcript_path, detected_language = self.transcribe_audio(audio_path, model_size, save_transcript=True)
        else:
            transcript, transcript_path, detected_language = self.transcribe_audio(audio_path, model_size, save_transcript=False)
        
        return transcript, audio_path, transcript_path, volume, detected_language 
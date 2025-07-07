import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

SAMPLE_RATE = 16000  # Sample rate
CHANNELS = 1         # Mono channel


def list_audio_devices():
    """List available audio devices with numbers"""
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        print(f"{idx}: {dev['name']} (Input channels: {dev['max_input_channels']}, Output channels: {dev['max_output_channels']})")
    return devices


def check_audio_levels(duration=3, device=None):
    """Check audio input levels"""
    print(f"Checking audio input levels for {duration} seconds...")
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=device)
    sd.wait()
    
    # Calculate volume
    volume = np.sqrt(np.mean(audio**2))
    print(f"Detected volume level: {volume}")
    
    if volume < 30:  # Threshold can be adjusted
        print("Warning: Volume too low, may not detect audio input")
        return False
    return True


def record_audio(duration=5, output_path="output.wav", device=None):
    print(f"Starting recording for {duration} seconds...")
    print("Please start speaking...")
    
    # Record audio
    audio = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16', device=device)
    sd.wait()  # Wait for recording to finish
    
    # Check recording quality
    volume = np.sqrt(np.mean(audio**2))
    print(f"Recording completed, volume level: {volume}")
    
    if volume < 20:
        print("Warning: Recording volume too low, please check microphone settings")
    
    # Save file
    write(output_path, SAMPLE_RATE, audio)
    print(f"Recording saved to {output_path}")
    
    return audio


def main():
    print("=== Talkie-Codie Recording Tool ===")
    
    # List audio devices
    devices = list_audio_devices()
    print()
    
    # Check audio input
    device_idx = input("Please enter the input device number you want to use (default Enter for system default): ")
    if device_idx.strip() == "":
        device = None
    else:
        try:
            device = int(device_idx)
            if device < 0 or device >= len(devices):
                print("Device number out of range, using default device.")
                device = None
        except ValueError:
            print("Invalid input, using default device.")
            device = None
    
    if not check_audio_levels(2, device=device):
        print("Please check microphone connection and system permission settings")
        return
    
    duration = input("Please enter recording duration (seconds, default 5): ")
    try:
        duration = float(duration)
    except ValueError:
        duration = 5
    duration = int(duration)  # Fix type error
    
    output_path = input("Please enter save filename (default output.wav): ") or "output.wav"
    
    record_audio(duration, output_path, device=device)


if __name__ == "__main__":
    main() 
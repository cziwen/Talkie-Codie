#!/usr/bin/env python3
"""
Talkie-Codie main program
Complete speech-to-text workflow with LLM optimization
"""

import sys
import os

# Add project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.audio.core import AudioProcessor
from src.llm.manager import LLMManager

def main():
    """Main program entry point"""
    print("=== Talkie-Codie Speech-to-Text Tool ===")
    print("Convert your speech to text and optimize it to better prompt using LLM\n")
    
    # Initialize audio processor
    processor = AudioProcessor()
    
    # Initialize LLM manager
    llm_manager = LLMManager()
    
    # Check LLM configuration
    if not llm_manager.current_provider:
        print("LLM provider not configured, will skip prompt optimization step")
        print("Please configure config/llm_config.json file")
        use_llm = False
    else:
        print(f"Current LLM provider: {llm_manager.get_current_provider_info()}")
        use_llm = True
    
    # List audio devices
    devices = processor.list_audio_devices()
    print()
    
    # Select audio device
    device_idx = input("Please enter the input device number you want to use (default Enter for system default): ")
    device = None
    if device_idx.strip():
        try:
            device = int(device_idx)
            if device < 0 or device >= len(devices):
                print("Device number out of range, using default device.")
                device = None
        except ValueError:
            print("Invalid input, using default device.")
            device = None
    
    # Check audio input
    if not processor.check_audio_levels(2, device=device):
        print("Please check microphone connection and system permission settings")
        return
    
    # Set recording parameters
    duration = input("Please enter recording duration (seconds, default 5): ")
    try:
        duration = float(duration)
    except ValueError:
        duration = 5
    duration = int(duration)
    
    # Select Whisper model
    print("\nAvailable Whisper model sizes:")
    print("tiny: Fastest, lower accuracy")
    print("base: Balanced speed and accuracy (recommended)")
    print("small: More accurate, slightly slower")
    print("medium: High accuracy, slower")
    print("large: Highest accuracy, slowest")
    
    model_size = input("Please select model size (default base): ").strip() or "base"
    
    # Ask whether to use custom filename
    use_custom_name = input("Use custom filename? (y/n, default n): ").lower().strip() in ['y', 'yes']
    output_path = None
    if use_custom_name:
        custom_name = input("Please enter custom filename (without extension): ").strip()
        if custom_name:
            output_path = f"cache/audio/{custom_name}.wav"
    
    try:
        # Execute complete recording and transcription workflow
        transcript, audio_path, transcript_path, volume, detected_language = processor.record_and_transcribe(
            duration=duration,
            model_size=model_size,
            device=device,
            output_path=output_path
        )
        
        print(f"\n=== Transcription Result ===")
        print(transcript)
        if detected_language:
            print(f"Detected language: {detected_language}")
        
        # LLM optimization
        if use_llm:
            print(f"\n=== LLM Optimization ===")
            
            # Select task type
            print("Please select task type:")
            print("1. general - General optimization")
            print("2. coding - Programming related")
            print("3. writing - Writing related")
            print("4. analysis - Analysis related")
            
            task_choice = input("Please select task type (1-4, default 1): ").strip() or "1"
            task_types = {"1": "general", "2": "coding", "3": "writing", "4": "analysis"}
            task_type = task_types.get(task_choice, "general")
            
            print(f"Using task type: {task_type}")
            
            # Select optimization level
            print("\nPlease select optimization level:")
            print("1. default - Concise optimization")
            print("2. pro - Professional optimization")
            
            level_choice = input("Please select level (1-2, default 1): ").strip() or "1"
            levels = {"1": "default", "2": "pro"}
            level = levels.get(level_choice, "default")
            
            print(f"Using level: {level}")
            print("Optimizing prompt...")
            
            result = llm_manager.optimize_prompt(transcript, task_type, level, language=detected_language)
            
            # Process return result
            if isinstance(result, tuple):
                optimized_prompt, optimized_path = result
            else:
                optimized_prompt = result
                optimized_path = None
            
            print(f"\n=== Optimized Prompt ===")
            print(optimized_prompt)
        
        print(f"\n=== Workflow Completed ===")
        print("Audio file:", audio_path)
        if transcript_path:
            print("Transcription file:", transcript_path)
        if use_llm and optimized_path:
            print("Optimized file:", optimized_path)
        
        # Ask whether to continue
        while True:
            choice = input("\nContinue recording and transcription? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                print("\n" + "="*50 + "\n")
                main()  # Recursive call, restart
                break
            elif choice in ['n', 'no']:
                print("Thank you for using Talkie-Codie!")
                break
            else:
                print("Please enter y or n")
        
    except Exception as e:
        print(f"Error occurred during program execution: {e}")
        print("Please check if audio file exists, or run the program again.")

if __name__ == "__main__":
    main() 
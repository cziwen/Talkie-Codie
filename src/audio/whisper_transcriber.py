from faster_whisper import WhisperModel
import os
import json

def load_whisper_config():
    """
    Load whisper configuration file
    
    Returns:
        dict: Configuration dictionary
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
                # Merge default config and user config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except Exception as e:
            print(f"Failed to read config file: {e}, using default config")
            return default_config
    else:
        print("Config file not found, using default config")
        return default_config

def transcribe_audio(audio_path, model_size=None):
    """
    Transcribe audio file using faster-whisper
    
    Args:
        audio_path (str): Audio file path
        model_size (str): Model size ("tiny", "base", "small", "medium", "large")
    
    Returns:
        tuple: (Transcribed text, detected language)
    """
    # Load configuration
    config = load_whisper_config()
    
    # If model_size parameter is passed, override the setting in config file
    if model_size:
        config["model_size"] = model_size
    
    print(f"Loading Whisper model: {config['model_size']}")
    print(f"Using device: {config['device']}")
    print(f"Compute type: {config['compute_type']}")
    
    # Load model (will download on first run)
    model = WhisperModel(
        config["model_size"], 
        device=config["device"], 
        compute_type=config["compute_type"]
    )
    
    print(f"Starting transcription of audio file: {audio_path}")
    
    # Prepare transcription parameters
    transcribe_kwargs = {
        "beam_size": config["beam_size"],
        "task": config["task"]
    }
    
    # If language is specified, add to parameters
    if config["language"]:
        transcribe_kwargs["language"] = config["language"]
    
    # If VAD filtering is enabled, add to parameters
    if config["vad_filter"]:
        transcribe_kwargs["vad_filter"] = True
        transcribe_kwargs["vad_parameters"] = config["vad_parameters"]
    
    # Transcribe audio
    segments, info = model.transcribe(audio_path, **transcribe_kwargs)
    
    # Collect transcription results
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
    
    print(f"Transcription completed!")
    print(f"Detected language: {info.language} (confidence: {info.language_probability:.2f})")
    
    return transcript.strip(), info.language

def main():
    print("=== Talkie-Codie Speech Transcription Tool ===")
    
    # Check if recording file exists
    if os.path.exists("output.wav"):
        audio_path = "output.wav"
        print(f"Found recording file: {audio_path}")
    else:
        audio_path = input("Please enter audio file path: ")
        if not os.path.exists(audio_path):
            print("File not found!")
            return
    
    # Select model size
    print("\nAvailable model sizes:")
    print("tiny: Fastest, lower accuracy")
    print("base: Balanced speed and accuracy (recommended)")
    print("small: More accurate, slightly slower")
    print("medium: High accuracy, slower")
    print("large: Highest accuracy, slowest")
    
    model_size = input("Please select model size (default base): ").strip() or "base"
    
    # Transcribe
    try:
        transcript, detected_language = transcribe_audio(audio_path, model_size)
        print(f"\nTranscription result:\n{transcript}")
        print(f"Detected language: {detected_language}")
        
        # Save transcription result
        output_file = audio_path.replace(".wav", "_transcript.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(transcript)
        print(f"\nTranscription result saved to: {output_file}")
        
    except Exception as e:
        print(f"Error occurred during transcription: {e}")

if __name__ == "__main__":
    main() 
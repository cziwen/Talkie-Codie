![Talkie-Codie Banner](assets/images/Banner.png)

# Talkie-Codie
Voice to prompt, best for vibe coding

[English](README.md) | [中文](README_CN.md)

## 🎥 Demo Video
Watch the demo to see Talkie-Codie in action:

[![Talkie-Codie Demo](https://img.youtube.com/vi/oUjS5hgegiQ/0.jpg)](https://youtu.be/oUjS5hgegiQ)

A cross-platform desktop application that converts your voice into optimized prompts using AI-powered speech recognition and language model enhancement.

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Microphone access

### Run Application

1. **Optional: Create virtual environment**
   ```bash
   # Using conda
   conda create -n talkie-codie python=3.10
   conda activate talkie-codie
   
   # Or using venv
   python -m venv talkie-codie
   source talkie-codie/bin/activate  # On Windows: talkie-codie\Scripts\activate
   ```

2. **Launch GUI (auto-installs dependencies)**
   ```bash
   python run_gui.py
   ```

**Note**: First startup may be slow due to model downloads. Configure your API key in the GUI settings.

**Note**: Without API configuration, the app will only use Whisper for audio-to-text conversion.

### Configuration

All settings can be configured through the GUI:
- **LLM Provider & API Key**: OpenAI or DeepSeek
- **Whisper Settings**: Device, model size, compute type
- **Audio Device**: Select your microphone

### Command Line Mode
```bash
python src/main.py
```

## Usage

1. **Select Input Device**: Choose your microphone from the dropdown
2. **Start Recording**: Click the record button to begin voice capture
3. **View Results**: See your transcribed text and AI-enhanced prompt
4. **Copy Output**: Use the copy button to copy the optimized prompt
5. **Settings**: Access configuration options via the settings button

### Cache Management

```bash
# View cache information
python scripts/clear_cache.py info

# Clear cache (with confirmation)
python scripts/clear_cache.py clear

# Force clear cache
python scripts/clear_cache.py clear-force
```

## Dependencies

- **PyQt6**: Modern GUI framework
- **sounddevice**: Audio recording and playback
- **faster-whisper**: Speech-to-text transcription
- **scipy/numpy**: Scientific computing
- **requests**: HTTP client for API calls

## Troubleshooting

### Common Issues

1. **No audio input detected**
   - Check microphone permissions
   - Verify device selection in settings
   - Ensure microphone is not muted

2. **LLM API errors**
   - Verify API key is correct
   - Check internet connection
   - Ensure sufficient API credits

3. **Whisper model download issues**
   - Check internet connection
   - Verify sufficient disk space
   - Try different model size in settings

---

**Note**: This application requires an active internet connection for LLM API calls and initial Whisper model downloads.

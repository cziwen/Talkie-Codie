# Talkie-Codie
Voice to prompt, empowering your vibe coding

A cross-platform desktop application that converts your voice into optimized prompts using AI-powered speech recognition and language model enhancement.

## Features

- **Voice Recording**: High-quality audio recording with real-time waveform visualization
- **Speech-to-Text**: Powered by Whisper for accurate speech transcription
- **AI Enhancement**: LLM-powered prompt optimization and rephrasing
- **Cross-Platform**: Works on Windows and macOS
- **Modern GUI**: Clean PyQt6 interface with intuitive controls
- **Settings Management**: Easy configuration for audio devices and LLM providers

## Quick Start

### Prerequisites
- Python 3.10 or higher
- Microphone access

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Talkie-Codie
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure LLM API**
   - Copy the config template: `cp config/llm_config.json config/llm_config.json.backup`
   - Edit `config/llm_config.json` and add your API key
   - Supported providers: OpenAI, DeepSeek

4. **Configure Whisper (Optional)**
   ```bash
   python scripts/configure_whisper.py
   ```

### Running the Application

#### GUI Mode (Recommended)
```bash
# Auto-install dependencies and launch
python run_gui.py

# Or launch directly
python src/main_gui.py
```

#### Command Line Mode
```bash
python src/main.py
```

## Usage

### Main Interface

1. **Select Input Device**: Choose your microphone from the dropdown
2. **Start Recording**: Click the record button to begin voice capture
3. **View Results**: See your transcribed text and AI-enhanced prompt
4. **Copy Output**: Use the copy button to copy the optimized prompt
5. **Settings**: Access configuration options via the settings button

### Recording Features

- **Real-time Visualization**: See audio waveform during recording
- **Auto-stop**: Automatically stops after 60 seconds or when silence is detected
- **High Quality**: 44.1kHz sampling rate for optimal transcription

### Settings Configuration

Access settings to configure:
- **LLM Provider**: Choose between OpenAI and DeepSeek
- **API Key**: Set your API credentials
- **Whisper Device**: CPU/CUDA/MPS inference device
- **Model Size**: tiny/base/small/medium/large
- **Compute Type**: int8/int16/float16/float32
- **Input Device**: Select your preferred microphone

### Cache Management

```bash
# View cache information
python scripts/clear_cache.py info

# Clear cache (with confirmation)
python scripts/clear_cache.py clear

# Force clear cache
python scripts/clear_cache.py clear-force
```

## Project Structure

```
Talkie-Codie/
├── src/                    # Main application code
│   ├── audio/             # Audio processing modules
│   ├── llm/               # Language model integration
│   ├── ui/                # User interface components
│   └── main_gui.py        # Main GUI application
├── config/                # Configuration files
├── scripts/               # Utility scripts
├── assets/                # Icons and sounds
├── docs/                  # Documentation
└── cache/                 # Temporary files
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

### Getting Help

- Check the documentation in `docs/` folder
- Review configuration guides for detailed setup instructions
- Ensure all dependencies are properly installed

## Development

For development and extension:
- Review source code comments for API integration
- Check `docs/` folder for technical documentation
- Follow the existing code structure for consistency

---

**Note**: This application requires an active internet connection for LLM API calls and initial Whisper model downloads.

# Audio Dependencies Setup Guide

## ⚠️ IMPORTANT: Audio Library Installation Required

Talkie-Codie requires **PortAudio** for audio recording functionality. You may encounter "PortAudio library not found" errors if system-level audio libraries are not installed.

## Platform-Specific Installation

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

### macOS
```bash
# Using Homebrew
brew install portaudio

# Or using MacPorts
sudo port install portaudio
```

### Windows
- Usually works out of the box with pip install
- If you encounter issues, try: `pip install pyaudio`

### WSL (Windows Subsystem for Linux)
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

## After Installing System Dependencies

Reinstall sounddevice to ensure proper linking:
```bash
pip uninstall sounddevice
pip install sounddevice
```

## Verification

Test if audio libraries are properly installed:
```python
import sounddevice as sd
print("PortAudio version:", sd.get_portaudio_version())
print("Available devices:", sd.query_devices())
```

## Troubleshooting

### Common Issues

1. **"PortAudio library not found"**
   - Install system audio libraries for your platform (see above)
   - Reinstall sounddevice after system library installation

2. **No audio devices detected**
   - Check microphone permissions
   - Ensure audio drivers are installed
   - Try restarting your system

3. **WSL audio issues**
   - Ensure WSL2 is being used
   - Check Windows audio services are running
   - Consider running the app directly in Windows

### Alternative Solutions

If you continue having issues with sounddevice, you can try using pyaudio instead:
```bash
pip install pyaudio
```

---

**Note**: This setup is required for the audio recording functionality. Without proper audio library installation, the application will not be able to record voice input. 
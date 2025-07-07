# 音频依赖安装指南

## ⚠️ 重要：需要安装音频库

Talkie-Codie 需要 **PortAudio** 来实现音频录制功能。如果未安装系统级音频库，您可能会遇到 "PortAudio library not found" 错误。

## 各平台安装方法

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

### macOS
```bash
# 使用 Homebrew
brew install portaudio

# 或使用 MacPorts
sudo port install portaudio
```

### Windows
- 通常通过 pip install 即可正常工作
- 如果遇到问题，尝试: `pip install pyaudio`

### WSL (Windows Subsystem for Linux)
```bash
sudo apt update
sudo apt install portaudio19-dev python3-pyaudio
```

## 安装系统依赖后

重新安装 sounddevice 以确保正确链接：
```bash
pip uninstall sounddevice
pip install sounddevice
```

## 验证安装

测试音频库是否正确安装：
```python
import sounddevice as sd
print("PortAudio 版本:", sd.get_portaudio_version())
print("可用设备:", sd.query_devices())
```

## 故障排除

### 常见问题

1. **"PortAudio library not found"**
   - 为您的平台安装系统音频库（见上文）
   - 安装系统库后重新安装 sounddevice

2. **未检测到音频设备**
   - 检查麦克风权限
   - 确保音频驱动程序已安装
   - 尝试重启系统

3. **WSL 音频问题**
   - 确保使用 WSL2
   - 检查 Windows 音频服务是否正在运行
   - 考虑直接在 Windows 中运行应用程序

### 替代解决方案

如果 sounddevice 持续出现问题，可以尝试使用 pyaudio：
```bash
pip install pyaudio
```

---

**注意**: 此设置是音频录制功能所必需的。没有正确的音频库安装，应用程序将无法录制语音输入。 
# Talkie-Codie
语音转提示词，赋能你的编程体验

一个跨平台桌面应用程序，使用AI驱动的语音识别和语言模型增强，将您的语音转换为优化的提示词。

## 功能特性

- **语音录制**: 高质量音频录制，实时波形可视化
- **语音转文字**: 基于Whisper的准确语音转录
- **AI增强**: LLM驱动的提示词优化和重新表述
- **跨平台**: 支持Windows和macOS
- **现代GUI**: 简洁的PyQt6界面，直观的控制
- **设置管理**: 音频设备和LLM提供商的简单配置

## 快速开始

### 环境要求
- Python 3.10 或更高版本
- 麦克风访问权限

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone <repository-url>
   cd Talkie-Codie
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置LLM API**
   - 复制配置模板: `cp config/llm_config.json config/llm_config.json.backup`
   - 编辑 `config/llm_config.json` 并添加您的API密钥
   - 支持的提供商: OpenAI, DeepSeek

4. **配置Whisper（可选）**
   ```bash
   python scripts/configure_whisper.py
   ```

### 运行应用程序

#### 图形界面模式（推荐）
```bash
# 自动安装依赖并启动
python run_gui.py

# 或直接启动
python src/main_gui.py
```

#### 命令行模式
```bash
python src/main.py
```

## 使用方法

### 主界面

1. **选择输入设备**: 从下拉菜单中选择您的麦克风
2. **开始录音**: 点击录音按钮开始语音捕获
3. **查看结果**: 查看转录文本和AI增强的提示词
4. **复制输出**: 使用复制按钮复制优化的提示词
5. **设置**: 通过设置按钮访问配置选项

### 录音功能

- **实时可视化**: 录音时查看音频波形
- **自动停止**: 60秒后或检测到静音时自动停止
- **高质量**: 44.1kHz采样率，确保最佳转录效果

### 设置配置

访问设置以配置：
- **LLM提供商**: 在OpenAI和DeepSeek之间选择
- **API密钥**: 设置您的API凭据
- **Whisper设备**: CPU/CUDA/MPS推理设备
- **模型大小**: tiny/base/small/medium/large
- **计算类型**: int8/int16/float16/float32
- **输入设备**: 选择您偏好的麦克风

### 缓存管理

```bash
# 查看缓存信息
python scripts/clear_cache.py info

# 清理缓存（需要确认）
python scripts/clear_cache.py clear

# 强制清理缓存
python scripts/clear_cache.py clear-force
```

## 项目结构

```
Talkie-Codie/
├── src/                    # 主应用程序代码
│   ├── audio/             # 音频处理模块
│   ├── llm/               # 语言模型集成
│   ├── ui/                # 用户界面组件
│   └── main_gui.py        # 主GUI应用程序
├── config/                # 配置文件
├── scripts/               # 实用脚本
├── assets/                # 图标和声音
├── docs/                  # 文档
└── cache/                 # 临时文件
```

## 依赖项

- **PyQt6**: 现代GUI框架
- **sounddevice**: 音频录制和播放
- **faster-whisper**: 语音转文字转录
- **scipy/numpy**: 科学计算
- **requests**: API调用的HTTP客户端

## 故障排除

### 常见问题

1. **未检测到音频输入**
   - 检查麦克风权限
   - 验证设置中的设备选择
   - 确保麦克风未静音

2. **LLM API错误**
   - 验证API密钥是否正确
   - 检查网络连接
   - 确保有足够的API额度

3. **Whisper模型下载问题**
   - 检查网络连接
   - 验证有足够的磁盘空间
   - 尝试在设置中使用不同的模型大小

### 获取帮助

- 查看 `docs/` 文件夹中的文档
- 查看配置指南了解详细设置说明
- 确保所有依赖项都已正确安装

## 开发

对于开发和扩展：
- 查看源代码注释了解API集成
- 查看 `docs/` 文件夹了解技术文档
- 遵循现有代码结构以保持一致性

---

**注意**: 此应用程序需要活跃的网络连接来进行LLM API调用和初始Whisper模型下载。 
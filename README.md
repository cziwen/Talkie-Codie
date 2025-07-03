# Talkie-Codie
Voice to prompt, empowering your vibe coding

## 项目目标
开发一个跨平台的独立应用（支持 Windows 和 macOS），将用户语音转换为自然语言 prompt。

## 技术方案简述

- **语音识别模块**：使用 [fast-Whisper](https://github.com/SYSTRAN/faster-whisper) 作为后端，将音频转写为文本。
- **大模型调用模块**：默认使用 DeepSeek API，将 Whisper 转换的文本送入大模型进行 prompt 优化（如摘要、润色等）。
- **格式化输出**：使用结构化标签格式（`<REPHRASE>`、`<SUMMARY>`），便于程序解析和提取。
- **部署平台**：独立 App，兼容 Windows 和 macOS。

## 快速开始

### 环境准备
```bash
# 创建 conda 环境
conda create -y -n talkie-codie python=3.10
conda activate talkie-codie

# 安装依赖
pip install -r requirements.txt
```

### 配置 LLM
1. 复制配置文件：`cp config/llm_config.json config/llm_config.json.backup`
2. 编辑 `config/llm_config.json`，填入你的 API 密钥
3. 详细配置请参考 [LLM 配置指南](docs/LLM_SETUP.md)

### 配置 Whisper（可选）
1. 运行配置工具：`python scripts/configure_whisper.py`
2. 选择设备类型（CPU/CUDA）和其他参数
3. 详细配置请参考 [Whisper 配置指南](docs/WHISPER_CONFIG.md)

### 优化档位说明
- **default**：简洁优化，输出长度不超过原文，适合快速处理
- **pro**：专业优化，输出长度为原文的2-4倍，包含详细的技术规格和结构化内容

### 运行程序

#### 图形界面（推荐）
```bash
# 使用启动脚本（自动安装依赖）
python run_gui.py

# 或直接运行 GUI
python src/main_gui.py
```

### 界面功能说明

#### 主要功能
- **优化风格选择**：选择优化类型（代码生成、文档编写、问题解答、创意写作）
- **录音设备选择**：选择可用的音频输入设备
- **录音控制**：简洁的录音按钮，支持最长60秒录音
- **转录显示**：实时显示转录结果和优化结果（大面积文本区）
- **一键复制**：复制全部文本内容
- **设置管理**：音频设备、LLM配置、Whisper设置等

#### 命令行界面
```bash
# 完整流程（录音 + 转录 + LLM 优化）
python src/main.py
```

详细 GUI 使用说明请参考 [docs/GUI_GUIDE.md](docs/GUI_GUIDE.md)

### 缓存管理
```bash
# 显示缓存信息
python scripts/clear_cache.py info

# 清理缓存（需要确认）
python scripts/clear_cache.py clear

# 强制清理缓存
python scripts/clear_cache.py clear-force
```

## 目录结构简述

- `src/`：主程序代码（UI、音频、LLM等）
- `scripts/`：配置和缓存管理脚本
- `config/`：配置文件
- `assets/`：图标、声音等资源
- `docs/`：开发和使用文档
- `cache/`：缓存目录

## 重要变更
- 使用 PyQt6 构建现代化界面，提供更好的用户体验
- 简化界面布局，优化操作流程
- 只保留default/pro档位，优化风格和设备选择更直观
- 设备列表自动加载，无需刷新按钮

## 常见问题
- 见 [docs/GUI_GUIDE.md](docs/GUI_GUIDE.md)

---

如需开发/扩展API、LLM等，请参考文档和源码注释。

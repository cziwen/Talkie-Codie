# Whisper 配置说明

## 概述

Talkie-Codie 现在支持通过配置文件来设置 Whisper 语音转录的各种参数，包括设备类型（CPU/CUDA）、计算类型、模型大小等。

## 配置文件位置

配置文件位于 `config/whisper_config.json`

## 配置参数说明

### 基本参数

- **device**: 设备类型
  - `"cpu"`: 使用CPU（推荐用于低配置设备）
  - `"cuda"`: 使用GPU（推荐用于有NVIDIA GPU的设备）

- **compute_type**: 计算类型
  - `"int8"`: 最快，内存占用最少，精度较低
  - `"int16"`: 平衡速度和精度
  - `"float16"`: 较高精度，需要更多内存
  - `"float32"`: 最高精度，需要最多内存

- **model_size**: 模型大小
  - `"tiny"`: 最快，准确度较低，约39MB
  - `"base"`: 平衡速度和准确度，约74MB（推荐）
  - `"small"`: 更准确，稍慢，约244MB
  - `"medium"`: 高准确度，较慢，约769MB
  - `"large"`: 最高准确度，最慢，约1550MB

### 高级参数

- **beam_size**: 束搜索大小（1-10，默认5）
- **language**: 语言代码（如"zh", "en"，null为自动检测）
- **task**: 任务类型（"transcribe"或"translate"）
- **vad_filter**: 是否启用语音活动检测过滤
- **vad_parameters**: VAD参数设置

## 使用方法

### 1. 使用配置管理工具（推荐）

运行配置管理工具进行交互式配置：

```bash
python scripts/configure_whisper.py
```

该工具会引导你完成所有配置选项的设置。

### 2. 手动编辑配置文件

直接编辑 `config/whisper_config.json` 文件：

```json
{
    "device": "cuda",
    "compute_type": "float16",
    "model_size": "base",
    "beam_size": 5,
    "language": null,
    "task": "transcribe",
    "vad_filter": true,
    "vad_parameters": {
        "min_silence_duration_ms": 500
    }
}
```

## 性能优化建议

### 低配置设备（CPU）
```json
{
    "device": "cpu",
    "compute_type": "int8",
    "model_size": "tiny"
}
```

### 中等配置设备（CPU）
```json
{
    "device": "cpu",
    "compute_type": "int16",
    "model_size": "base"
}
```

### 高配置设备（GPU）
```json
{
    "device": "cuda",
    "compute_type": "float16",
    "model_size": "small"
}
```

### 追求最高精度（GPU）
```json
{
    "device": "cuda",
    "compute_type": "float32",
    "model_size": "large"
}
```

## CUDA 支持

要使用 CUDA 加速，需要确保：

1. 安装了 NVIDIA GPU 驱动
2. 安装了 CUDA Toolkit
3. 安装了支持 CUDA 的 PyTorch 版本

可以通过以下命令检查 CUDA 是否可用：

```python
import torch
print(torch.cuda.is_available())
```

## 故障排除

### 配置文件不存在
如果配置文件不存在，系统会使用默认配置（CPU + int8 + base模型）。

### CUDA 不可用
如果选择 CUDA 但系统不支持，会自动回退到 CPU。

### 内存不足
如果遇到内存不足错误，可以：
1. 降低模型大小（如从 large 改为 base）
2. 降低计算类型（如从 float32 改为 int8）
3. 减少 beam_size

## 示例配置

### 中文语音转录优化
```json
{
    "device": "cuda",
    "compute_type": "float16",
    "model_size": "base",
    "language": "zh",
    "beam_size": 5,
    "vad_filter": true
}
```

### 英文语音转录优化
```json
{
    "device": "cuda",
    "compute_type": "float16",
    "model_size": "small",
    "language": "en",
    "beam_size": 5,
    "vad_filter": true
}
``` 
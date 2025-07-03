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
- **pro**：专业优化，输出长度为原文的2-10倍，包含详细的技术规格和结构化内容

### 运行程序
```bash
# 完整流程（录音 + 转录 + LLM 优化）
python src/main.py

# 测试新的格式化功能
python src/test_new_format.py
```

### 缓存管理
```bash
# 显示缓存信息
python scripts/clear_cache.py info

# 清理缓存（需要确认）
python scripts/clear_cache.py clear

# 强制清理缓存
python scripts/clear_cache.py clear-force
```

## API 扩展方法

### 1. 创建新的 API 提供商

继承 `LLMProvider` 基类，实现必要的方法：

```python
# src/llm/your_api.py
from .base import LLMProvider
import requests

class YourAPIProvider(LLMProvider):
    """你的 API 提供商实现"""
    
    def __init__(self, config):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.your-service.com")
        self.model = config.get("model", "default")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """实现文本生成逻辑"""
        url = f"{self.base_url}/generate"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        data = {"prompt": prompt, **kwargs}
        
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def test_connection(self) -> bool:
        """实现连接测试"""
        try:
            response = self.generate("test", max_tokens=5)
            return len(response) > 0
        except:
            return False
```

### 2. 注册新的提供商

在 `LLMFactory` 中注册你的提供商：

```python
# src/llm/factory.py
from .your_api import YourAPIProvider

class LLMFactory:
    _providers = {
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
        "local": LocalProvider,
        "your_api": YourAPIProvider  # 添加你的提供商
    }
```

### 3. 配置新提供商

在配置文件中添加你的 API 配置：

```json
{
    "default_provider": "your_api",
    "providers": {
        "your_api": {
            "api_key": "your_api_key_here",
            "base_url": "https://api.your-service.com",
            "model": "your-model-name"
        }
    }
}
```

## 本地模型扩展方法

### 1. 支持新的本地 API 格式

如果本地模型使用不同的 API 格式，可以在 `LocalProvider` 中添加支持：

```python
# src/llm/local.py
def generate(self, prompt: str, **kwargs) -> str:
    # 添加新的端点格式
    endpoints = [
        f"{self.base_url}/v1/chat/completions",  # OpenAI 兼容
        f"{self.base_url}/chat/completions",     # 简化格式
        f"{self.base_url}/generate",             # 通用格式
        f"{self.base_url}/api/generate",         # 另一种格式
        f"{self.base_url}/your-custom-endpoint"  # 你的自定义端点
    ]
    
    # 添加新的请求格式
    request_formats = [
        # 现有格式...
        {
            "input": prompt,
            "custom_field": "value",  # 你的自定义字段
            "parameters": kwargs
        }
    ]
    
    # 添加新的响应格式解析
    if "custom_response_field" in result:
        return result["custom_response_field"]
```

### 2. 创建专门的本地提供商

对于特殊的本地模型，可以创建专门的提供商：

```python
# src/llm/ollama.py
from .base import LLMProvider
import requests

class OllamaProvider(LLMProvider):
    """Ollama 本地模型提供商"""
    
    def __init__(self, config):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:11434")
        self.model = config.get("model", "llama2")
    
    def generate(self, prompt: str, **kwargs) -> str:
        url = f"{self.base_url}/api/generate"
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            **kwargs
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()["response"]
    
    def test_connection(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """获取可用的 Ollama 模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except:
            pass
        return []
```

### 3. 支持自定义模型加载

```python
# src/llm/custom_local.py
from .base import LLMProvider
import subprocess
import json

class CustomLocalProvider(LLMProvider):
    """自定义本地模型提供商"""
    
    def __init__(self, config):
        super().__init__(config)
        self.model_path = config.get("model_path")
        self.process = None
    
    def _start_model(self):
        """启动本地模型进程"""
        if not self.process:
            cmd = [
                "python", "-m", "your_model_server",
                "--model", self.model_path,
                "--port", "8000"
            ]
            self.process = subprocess.Popen(cmd)
    
    def generate(self, prompt: str, **kwargs) -> str:
        self._start_model()
        # 实现与本地模型的通信逻辑
        # ...
    
    def __del__(self):
        if self.process:
            self.process.terminate()
```

## 项目结构

```
Talkie-Codie/
├── src/
│   ├── audio/              # 音频处理模块
│   │   ├── core.py         # 核心音频处理
│   │   ├── recorder.py     # 录音功能
│   │   └── whisper_transcriber.py  # 转录功能
│   ├── llm/                # LLM 模块
│   │   ├── base.py         # 基础抽象类
│   │   ├── factory.py      # 提供商工厂
│   │   ├── manager.py      # LLM 管理器
│   │   ├── deepseek.py     # DeepSeek API
│   │   ├── openai.py       # OpenAI API
│   │   └── local.py        # 本地模型支持
│   └── main.py             # 主程序
├── cache/                  # 缓存文件夹
│   ├── audio/              # 音频文件缓存
│   ├── transcripts/        # 转录文件缓存
│   └── optimized/          # 优化结果缓存
├── config/
│   └── llm_config.json     # LLM 配置文件
├── docs/
│   └── LLM_SETUP.md        # 配置指南
├── scripts/
│   └── clear_cache.py      # 缓存清理脚本
└── requirements.txt        # 依赖管理
```

## 贡献指南

1. Fork 项目
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -am 'Add your feature'`
4. 推送分支：`git push origin feature/your-feature`
5. 创建 Pull Request

## 许可证

MIT License

---

后续将逐步开发具体功能模块，欢迎参与和贡献！

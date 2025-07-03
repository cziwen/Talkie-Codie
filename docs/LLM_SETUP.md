# LLM 配置指南

## 概述

Talkie-Codie 支持多种 LLM 提供商，包括：
- **DeepSeek** (默认)
- **OpenAI**
- **本地部署模型**

## 配置步骤

### 1. 复制配置文件

```bash
cp config/llm_config.json config/llm_config.json.backup
```

### 2. 编辑配置文件

编辑 `config/llm_config.json` 文件，填入你的 API 密钥：

#### DeepSeek 配置
```json
{
    "default_provider": "deepseek",
    "providers": {
        "deepseek": {
            "api_key": "your_deepseek_api_key_here",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat"
        }
    }
}
```

#### OpenAI 配置
```json
{
    "default_provider": "openai",
    "providers": {
        "openai": {
            "api_key": "your_openai_api_key_here",
            "base_url": "https://api.openai.com/v1",
            "model": "gpt-3.5-turbo"
        }
    }
}
```

#### 本地模型配置
```json
{
    "default_provider": "local",
    "providers": {
        "local": {
            "base_url": "http://localhost:8000",
            "model": "default",
            "api_key": null
        }
    }
}
```

### 3. 获取 API 密钥

#### DeepSeek API
1. 访问 [DeepSeek 官网](https://platform.deepseek.com/)
2. 注册账号并登录
3. 在控制台获取 API 密钥

#### OpenAI API
1. 访问 [OpenAI 官网](https://platform.openai.com/)
2. 注册账号并登录
3. 在 API Keys 页面获取密钥

### 4. 测试配置

运行测试脚本验证配置：

```bash
python src/test_llm.py
```

## 本地模型部署

### 使用 Ollama

1. 安装 Ollama: https://ollama.ai/
2. 启动服务：
```bash
ollama serve
```

3. 下载模型：
```bash
ollama pull llama2
```

4. 配置为本地模型：
```json
{
    "default_provider": "local",
    "providers": {
        "local": {
            "base_url": "http://localhost:11434",
            "model": "llama2",
            "api_key": null
        }
    }
}
```

### 使用其他本地 API

支持任何兼容 OpenAI API 格式的本地服务，如：
- vLLM
- Text Generation WebUI
- LM Studio

## 故障排除

### 401 Unauthorized 错误
- 检查 API 密钥是否正确
- 确认 API 密钥有足够的余额
- 验证 API 端点是否正确

### 连接超时
- 检查网络连接
- 确认 API 服务是否可用
- 尝试增加超时时间

### 本地模型连接失败
- 确认本地服务是否启动
- 检查端口是否正确
- 验证 API 格式是否兼容

## 安全注意事项

1. **不要提交 API 密钥到版本控制**
2. **使用环境变量存储敏感信息**
3. **定期轮换 API 密钥**
4. **监控 API 使用量**

## 环境变量配置

你也可以使用环境变量配置 API 密钥：

```bash
export DEEPSEEK_API_KEY="your_api_key_here"
export OPENAI_API_KEY="your_api_key_here"
```

然后在配置文件中使用：

```json
{
    "providers": {
        "deepseek": {
            "api_key": "${DEEPSEEK_API_KEY}",
            "base_url": "https://api.deepseek.com/v1",
            "model": "deepseek-chat"
        }
    }
}
``` 
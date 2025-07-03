import requests
import json
from typing import Dict, Any, Optional
from .base import LLMProvider

class LocalProvider(LLMProvider):
    """本地部署模型提供商实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.base_url = config.get("base_url", "http://localhost:8000")
        self.model = config.get("model", "default")
        self.api_key = config.get("api_key")  # 可选，用于本地 API 认证
        
        if not self.base_url:
            raise ValueError("本地模型 API 端点未提供")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        使用本地模型生成文本
        
        Args:
            prompt: 输入提示词
            **kwargs: 其他参数
        
        Returns:
            生成的文本响应
        """
        # 尝试不同的本地 API 格式
        endpoints = [
            f"{self.base_url}/v1/chat/completions",  # OpenAI 兼容格式
            f"{self.base_url}/chat/completions",     # 简化格式
            f"{self.base_url}/generate",             # 通用格式
            f"{self.base_url}/api/generate"          # 另一种通用格式
        ]
        
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # 尝试不同的请求格式
        request_formats = [
            # OpenAI 兼容格式
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            # 简化格式
            {
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens
            },
            # 通用格式
            {
                "input": prompt,
                "parameters": {
                    "temperature": temperature,
                    "max_new_tokens": max_tokens
                }
            }
        ]
        
        for endpoint in endpoints:
            for request_format in request_formats:
                try:
                    response = requests.post(
                        endpoint, 
                        headers=headers, 
                        json=request_format, 
                        timeout=60
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    # 尝试不同的响应格式
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    elif "response" in result:
                        return result["response"]
                    elif "output" in result:
                        return result["output"]
                    elif "text" in result:
                        return result["text"]
                    elif "generated_text" in result:
                        return result["generated_text"]
                    elif isinstance(result, str):
                        return result
                        
                except (requests.exceptions.RequestException, KeyError, ValueError):
                    continue
        
        raise Exception("无法连接到本地模型或响应格式不支持")
    
    def test_connection(self) -> bool:
        """测试本地模型连接"""
        try:
            test_prompt = "Hello, this is a test message."
            response = self.generate(test_prompt, max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"本地模型连接测试失败: {e}")
            return False
    
    def get_available_models(self) -> list:
        """获取可用的本地模型列表"""
        try:
            response = requests.get(f"{self.base_url}/v1/models", timeout=10)
            if response.status_code == 200:
                result = response.json()
                return [model["id"] for model in result.get("data", [])]
        except:
            pass
        
        # 如果无法获取模型列表，返回默认模型
        return [self.model] 
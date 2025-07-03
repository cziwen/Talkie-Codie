import requests
import json
from typing import Dict, Any, Optional
from .base import LLMProvider

class OpenAIProvider(LLMProvider):
    """OpenAI API 提供商实现"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.model = config.get("model", "gpt-3.5-turbo")
        
        if not self.api_key:
            raise ValueError("OpenAI API 密钥未提供")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        使用 OpenAI API 生成文本
        
        Args:
            prompt: 输入提示词
            **kwargs: 其他参数
        
        Returns:
            生成的文本响应
        """
        url = f"{self.base_url}/chat/completions"
        
        # 设置默认参数
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 1000)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"OpenAI API 请求失败: {e}")
        except KeyError as e:
            raise Exception(f"OpenAI API 响应格式错误: {e}")
        except Exception as e:
            raise Exception(f"OpenAI API 调用失败: {e}")
    
    def test_connection(self) -> bool:
        """测试 OpenAI API 连接"""
        try:
            test_prompt = "Hello, this is a test message."
            response = self.generate(test_prompt, max_tokens=10)
            return len(response) > 0
        except Exception as e:
            print(f"OpenAI API 连接测试失败: {e}")
            return False 
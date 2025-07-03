from typing import Dict, Any, Type
from .base import LLMProvider
from .deepseek import DeepSeekProvider
from .openai import OpenAIProvider
from .local import LocalProvider

class LLMFactory:
    """LLM 提供商工厂类"""
    
    _providers = {
        "deepseek": DeepSeekProvider,
        "openai": OpenAIProvider,
        "local": LocalProvider
    }
    
    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]):
        """注册新的 LLM 提供商"""
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, provider_type: str, config: Dict[str, Any]) -> LLMProvider:
        """
        创建 LLM 提供商实例
        
        Args:
            provider_type: 提供商类型 ("deepseek", "openai", "local")
            config: 配置字典
        
        Returns:
            LLM 提供商实例
        """
        if provider_type not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(f"不支持的提供商类型: {provider_type}。可用类型: {available}")
        
        provider_class = cls._providers[provider_type]
        return provider_class(config)
    
    @classmethod
    def get_available_providers(cls) -> list:
        """获取可用的提供商列表"""
        return list(cls._providers.keys())
    
    @classmethod
    def get_provider_info(cls, provider_type: str) -> Dict[str, Any]:
        """获取提供商信息"""
        if provider_type not in cls._providers:
            return {"error": f"提供商 {provider_type} 不存在"}
        
        provider_class = cls._providers[provider_type]
        return {
            "name": provider_type,
            "class": provider_class.__name__,
            "description": provider_class.__doc__ or "无描述"
        } 
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.llm.factory import LLMFactory
from src.llm.base import LLMProvider, PromptOptimizer

class LLMManager:
    """LLM 管理器，统一管理所有 LLM 相关功能"""
    
    def __init__(self, config_path: str = "config/llm_config.json", cache_dir: str = "cache"):
        self.config_path = config_path
        self.cache_dir = cache_dir
        self.config = self._load_config()
        self.current_provider = None
        self.prompt_optimizer = None
        self._initialize_provider()
        
        # 确保缓存目录存在
        self._ensure_cache_dirs()
    
    def _ensure_cache_dirs(self):
        """确保缓存目录存在"""
        optimized_dir = os.path.join(self.cache_dir, "optimized")
        os.makedirs(optimized_dir, exist_ok=True)
    
    def _generate_filename(self, prefix="", extension=".txt"):
        """生成带时间戳的文件名"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if prefix:
            return f"{prefix}_{timestamp}{extension}"
        return f"{timestamp}{extension}"
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if not os.path.exists(self.config_path):
            print(f"配置文件不存在: {self.config_path}")
            print("请复制 config/llm_config.json 并填入你的 API 密钥")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}
    
    def _initialize_provider(self):
        """初始化默认提供商"""
        self.current_provider = None  # 确保初始化前为 None
        self.prompt_optimizer = None
        if not self.config:
            return
        
        default_provider = self.config.get("default_provider", "deepseek")
        if isinstance(default_provider, str) and default_provider:
            try:
                self.set_provider(default_provider)
            except Exception as e:
                print(f"初始化默认提供商失败: {e}")
                self.current_provider = None
                self.prompt_optimizer = None
    
    def set_provider(self, provider_type: str) -> bool:
        """
        设置当前 LLM 提供商
        
        Args:
            provider_type: 提供商类型
        
        Returns:
            是否设置成功
        """
        if not isinstance(provider_type, str) or not provider_type or not self.config or "providers" not in self.config:
            print("配置文件中缺少 providers 配置")
            return False
        
        if provider_type not in self.config["providers"]:
            print(f"配置文件中缺少 {provider_type} 的配置")
            return False
        
        try:
            provider_config = self.config["providers"][provider_type]
            self.current_provider = LLMFactory.create_provider(provider_type, provider_config)
            self.prompt_optimizer = PromptOptimizer(self.current_provider)
            print(f"成功设置 LLM 提供商: {provider_type}")
            return True
        except Exception as e:
            print(f"设置 LLM 提供商失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试当前 LLM 提供商连接"""
        if not self.current_provider:
            print("未设置 LLM 提供商")
            return False
        
        return self.current_provider.test_connection()
    
    def optimize_prompt(self, transcript: str, task_type: Optional[str] = None, level: str = "default", save_result: bool = True, language: Optional[str] = None):
        """
        优化转录文本为更好的 prompt
        
        Args:
            transcript: 转录的文本
            task_type: 任务类型
            level: 优化档位 ("default", "pro")
            save_result: 是否保存结果到缓存
            language: 检测到的语言代码
        
        Returns:
            优化后的 prompt
        """
        if not self.prompt_optimizer:
            print("LLM 提供商未初始化，无法优化 prompt")
            return transcript
        
        if task_type is None:
            default_task_type = self.config.get("prompt_optimization", {}).get("default_task_type", "general")
            task_type = default_task_type if isinstance(default_task_type, str) else "general"
        
        try:
            optimized_prompt = self.prompt_optimizer.optimize_prompt(transcript, task_type, level, language)
            
            # 保存优化结果到缓存
            if save_result:
                optimized_filename = self._generate_filename("optimized", ".txt")
                optimized_path = os.path.join(self.cache_dir, "optimized", optimized_filename)
                with open(optimized_path, "w", encoding="utf-8") as f:
                    f.write(optimized_prompt)
                print(f"优化结果已保存到: {optimized_path}")
                return optimized_prompt, optimized_path
            
            return optimized_prompt
        except Exception as e:
            print(f"优化 prompt 失败: {e}")
            return transcript
    
    def summarize_text(self, transcript: str, max_length: int = 100) -> str:
        """
        总结转录文本
        
        Args:
            transcript: 转录的文本
            max_length: 最大长度
        
        Returns:
            总结后的文本
        """
        if not self.prompt_optimizer:
            print("LLM 提供商未初始化，无法总结文本")
            return transcript
        
        try:
            return self.prompt_optimizer.summarize_text(transcript, max_length)
        except Exception as e:
            print(f"总结文本失败: {e}")
            return transcript
    
    def get_available_providers(self) -> list:
        """获取可用的提供商列表"""
        return LLMFactory.get_available_providers()
    
    def get_current_provider_info(self) -> Dict[str, Any]:
        """获取当前提供商信息"""
        if not self.current_provider:
            return {"error": "未设置 LLM 提供商"}
        
        return self.current_provider.get_provider_info()
    
    def update_config(self, provider_type: str, config_updates: Dict[str, Any]):
        """更新配置文件"""
        if not self.config:
            self.config = {"providers": {}}
        
        if "providers" not in self.config:
            self.config["providers"] = {}
        
        if provider_type not in self.config["providers"]:
            self.config["providers"][provider_type] = {}
        
        self.config["providers"][provider_type].update(config_updates)
        
        # 保存配置文件
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)
        
        print(f"配置文件已更新: {self.config_path}")
    
    def reload_config(self):
        """重新加载配置文件并重新初始化提供商"""
        self.config = self._load_config()
        self._initialize_provider()
        print("LLM配置已重新加载") 
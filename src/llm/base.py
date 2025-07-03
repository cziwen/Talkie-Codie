from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

class LLMProvider(ABC):
    """LLM 提供商的基础抽象类"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化 LLM 提供商
        
        Args:
            config: 配置字典，包含 API 密钥、端点等信息
        """
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        生成文本响应
        
        Args:
            prompt: 输入提示词
            **kwargs: 其他参数（如温度、最大长度等）
        
        Returns:
            生成的文本响应
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        测试 API 连接
        
        Returns:
            连接是否成功
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """获取提供商信息"""
        return {
            "name": self.name,
            "config": {k: v for k, v in self.config.items() if k != "api_key"}
        }

class PromptOptimizer:
    """Prompt 优化器，用于处理转录文本"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
    
    def _calculate_max_tokens(self, input_text: str, level: str) -> int:
        """根据输入文本长度和档位计算最大 token 数"""
        input_length = len(input_text)
        
        if level == "default":
            # 默认档：token 少于等于原始input
            return min(input_length, 500)
        elif level == "pro":
            # pro档：给足够的token空间，确保能完整输出
            # 考虑到prompt本身很长，需要给更多空间
            return max(input_length * 5, 2000)
        else:
            return 500
    
    def optimize_prompt(self, transcript: str, task_type: str = "general", level: str = "default") -> str:
        """
        优化转录文本为更好的 prompt
        
        Args:
            transcript: 转录的文本
            task_type: 任务类型 ("general", "coding", "writing", "analysis")
            level: 优化档位 ("default", "pro")
        
        Returns:
            优化后的 prompt
        """
        max_tokens = self._calculate_max_tokens(transcript, level)
        
        # 基础模板
        base_template = f"原文：{transcript}\n\n"
        
        # 根据档位和任务类型构建优化提示
        if level == "default":
            # default 档：简洁优化
            task_instructions = {
                "general": "转换为简洁专业的表达，去除口语化词汇",
                "coding": "转换为简洁的技术需求，明确编程任务",
                "writing": "转换为简洁的写作指导，明确写作类型",
                "analysis": "转换为简洁的分析框架，明确分析目标"
            }
            
            requirements = [
                "保持原意不变",
                "使语言更加专业流畅",
                "控制输出长度不超过原文"
            ]
            
            prompt = f"""请将以下口语化描述{task_instructions.get(task_type, "转换为简洁专业的表达")}：

{base_template}要求：
{chr(10).join(f"{i+1}. {req}" for i, req in enumerate(requirements))}

<REPHRASE>
优化后的内容
</REPHRASE>"""
            
        else:  # pro 档
            # pro 档：专业详细
            task_formats = {
                "general": "专业的项目管理格式，包含需求分解、质量标准、风险评估",
                "coding": "软件工程标准格式，包含技术架构、性能要求、测试部署",
                "writing": "学术写作标准格式，包含写作大纲、引用格式、质量评估",
                "analysis": "数据分析标准格式，包含分析框架、统计方法、质量控制"
            }
            
            requirements = [
                f"使用{task_formats.get(task_type, '专业标准格式')}",
                "使用行业标准术语",
                "输出最多为原文的5倍"
            ]
            
            prompt = f"""请将以下需求转换为{task_formats.get(task_type, "非常专业的结构化文档")}：

{base_template}要求：
{chr(10).join(f"{i+1}. {req}" for i, req in enumerate(requirements))}

<REPHRASE>
优化后的内容
</REPHRASE>"""
        
        try:
            optimized_text = self.llm_provider.generate(prompt, temperature=0.3, max_tokens=max_tokens)
            # 使用正则表达式提取内容
            extracted_text = self._extract_rephrase_content(optimized_text)
            return extracted_text.strip()
        except Exception as e:
            print(f"优化过程中出现错误: {e}")
            return transcript  # 如果优化失败，返回原文
    
    def _extract_rephrase_content(self, text: str) -> str:
        """使用正则表达式提取 <REPHRASE> 标签中的内容"""
        import re
        
        # 宽松的正则表达式匹配
        patterns = [
            r'<REPHRASE>\s*(.*?)\s*</REPHRASE>',  # 标准格式
            r'<rephrase>\s*(.*?)\s*</rephrase>',  # 小写格式
            r'<Rephrase>\s*(.*?)\s*</Rephrase>',  # 首字母大写格式
            r'REPHRASE:\s*(.*?)(?=\n\n|\n$|$)',   # 冒号格式
            r'Rephrase:\s*(.*?)(?=\n\n|\n$|$)',   # 首字母大写冒号格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到标签，尝试清理常见的客套话
        return self._clean_output(text)
    
    def _clean_output(self, text: str) -> str:
        """清理输出文本，去除客套话"""
        # 去除常见的客套话开头
        common_prefixes = [
            "以下为", "以下是", "以下内容", "优化后的内容：", "优化结果：",
            "转换后的内容：", "转换结果：", "输出结果：", "结果如下：",
            "**优化后的 prompt：**", "**优化结果：**", "**输出：**"
        ]
        
        cleaned_text = text
        for prefix in common_prefixes:
            if cleaned_text.startswith(prefix):
                cleaned_text = cleaned_text[len(prefix):].strip()
        
        # 去除常见的客套话结尾
        common_suffixes = [
            "以上为优化结果。", "以上为转换结果。", "以上为输出内容。",
            "这就是优化后的内容。", "这就是转换结果。"
        ]
        
        for suffix in common_suffixes:
            if cleaned_text.endswith(suffix):
                cleaned_text = cleaned_text[:-len(suffix)].strip()
        
        return cleaned_text
    
    def summarize_text(self, transcript: str, max_length: int = 100) -> str:
        """
        总结转录文本
        
        Args:
            transcript: 转录的文本
            max_length: 最大长度
        
        Returns:
            总结后的文本
        """
        summary_prompt = f"""
请将以下文本总结为不超过 {max_length} 字的简洁版本：

{transcript}

请按以下格式输出：
<SUMMARY>
总结内容
</SUMMARY>
"""
        
        try:
            summary = self.llm_provider.generate(summary_prompt, temperature=0.2, max_tokens=200)
            extracted_summary = self._extract_summary_content(summary)
            return extracted_summary.strip()
        except Exception as e:
            print(f"总结过程中出现错误: {e}")
            return transcript[:max_length] + "..." if len(transcript) > max_length else transcript
    
    def _extract_summary_content(self, text: str) -> str:
        """使用正则表达式提取 <SUMMARY> 标签中的内容"""
        import re
        
        # 宽松的正则表达式匹配
        patterns = [
            r'<SUMMARY>\s*(.*?)\s*</SUMMARY>',  # 标准格式
            r'<summary>\s*(.*?)\s*</summary>',  # 小写格式
            r'<Summary>\s*(.*?)\s*</Summary>',  # 首字母大写格式
            r'SUMMARY:\s*(.*?)(?=\n\n|\n$|$)',   # 冒号格式
            r'Summary:\s*(.*?)(?=\n\n|\n$|$)',   # 首字母大写冒号格式
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # 如果没有找到标签，尝试清理常见的客套话
        return self._clean_output(text) 
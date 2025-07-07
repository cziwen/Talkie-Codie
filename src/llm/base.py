from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import json

class LLMProvider(ABC):
    """Base abstract class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize LLM provider
        
        Args:
            config: Configuration dictionary containing API key, endpoint, etc.
        """
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text response
        
        Args:
            prompt: Input prompt
            **kwargs: Other parameters (such as temperature, max length, etc.)
        
        Returns:
            Generated text response
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """
        Test API connection
        
        Returns:
            Whether connection is successful
        """
        pass
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": self.name,
            "config": {k: v for k, v in self.config.items() if k != "api_key"}
        }

class PromptOptimizer:
    """Prompt optimizer for processing transcribed text"""
    
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider

    def _calculate_max_tokens(self, input_text: str, level: str) -> int:
        """Calculate maximum token count based on input text length and level"""
        input_length = len(input_text)
        if level == "default":
            return min(input_length, 512)
        elif level == "pro":
            return max(input_length * 5, 2048)
        else:
            return 500

    def optimize_prompt(self, transcript: str, task_type: str = "general", level: str = "default", language: Optional[str] = None) -> str:
        """
        Optimize transcript into a better prompt. Output is wrapped in <REPHRASE> tags. All instructions in English and specify 'Rewrite in the same language.'
        """
        max_tokens = self._calculate_max_tokens(transcript, level)
        task_instructions = {
            "general": "Rewrite the following in a more professional and concise way. Rewrite in the same language.",
            "coding": "Rewrite the following as a clear programming requirement. Rewrite in the same language.",
            "writing": "Rewrite the following as a fluent writing guide. Rewrite in the same language.",
            "analysis": "Rewrite the following as a concise analysis requirement. Rewrite in the same language."
        }
        instruction = task_instructions.get(task_type, task_instructions["general"])
        
        # If language is detected, specify the language in the instruction
        if language:
            # Convert language code to language name
            language_names = {
                "zh": "Chinese",
                "en": "English", 
                "ja": "Japanese",
                "ko": "Korean",
                "fr": "French",
                "de": "German",
                "es": "Spanish",
                "it": "Italian",
                "pt": "Portuguese",
                "ru": "Russian",
                "ar": "Arabic",
                "hi": "Hindi"
            }
            language_name = language_names.get(language, language.upper())
            instruction = instruction.replace("Rewrite in the same language.", f"Rewrite in {language_name}.")
        
        prompt = f"{instruction}\n{transcript}\nOutput in the following format:\n<REPHRASE>\n[Your rewritten content here]\n</REPHRASE>"
        try:
            optimized_text = self.llm_provider.generate(prompt, temperature=0.3, max_tokens=max_tokens)
            return self._extract_rephrase_content(optimized_text).strip()
        except Exception as e:
            print(f"Error during optimization: {e}")
            return transcript

    def _extract_rephrase_content(self, text: str) -> str:
        """Directly return content, removing common polite phrases"""
        return self._clean_output(text)

    def _clean_output(self, text: str) -> str:
        common_prefixes = [
            "以下为", "以下是", "以下内容", "优化后的内容：", "优化结果：",
            "转换后的内容：", "转换结果：", "输出结果：", "结果如下：",
            "**优化后的 prompt：**", "**优化结果：**", "**输出：**"
        ]
        cleaned_text = text
        for prefix in common_prefixes:
            if cleaned_text.startswith(prefix):
                cleaned_text = cleaned_text[len(prefix):].strip()
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
        Summarize transcript (English prompt, specify same language)
        """
        summary_prompt = f"Summarize the following in no more than {max_length} characters. Summarize in the same language.\n{transcript}\nOutput in the following format:\n<SUMMARY>\n[Your summary here]\n</SUMMARY>"
        try:
            summary = self.llm_provider.generate(summary_prompt, temperature=0.2, max_tokens=200)
            return self._extract_summary_content(summary).strip()
        except Exception as e:
            print(f"Error during summarization: {e}")
            return transcript[:max_length] + "..." if len(transcript) > max_length else transcript

    def _extract_summary_content(self, text: str) -> str:
        return self._clean_output(text) 
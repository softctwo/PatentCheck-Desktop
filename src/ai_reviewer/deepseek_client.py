"""
DeepSeek API客户端封装
支持调用DeepSeek Chat模型进行专利审查
"""
import os
from typing import Optional, List, Dict
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv


class DeepSeekClient:
    """DeepSeek API客户端"""
    
    # DeepSeek API配置
    DEFAULT_BASE_URL = "https://api.deepseek.com"
    DEFAULT_MODEL = "deepseek-chat"
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        初始化DeepSeek客户端
        
        Args:
            api_key: API密钥，如果未提供则从环境变量读取
            base_url: API基础URL，默认使用DeepSeek官方地址
        """
        # 加载.env文件
        load_dotenv()
        
        # 获取API密钥
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未找到DeepSeek API密钥。请设置环境变量 DEEPSEEK_API_KEY 或在.env文件中配置"
            )
        
        # 初始化OpenAI客户端（DeepSeek兼容OpenAI API格式）
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """
        调用DeepSeek Chat API进行对话
        
        Args:
            messages: 消息列表，格式为 [{"role": "user/system/assistant", "content": "..."}]
            model: 使用的模型名称
            temperature: 温度参数，控制输出的随机性 (0.0-2.0)
            max_tokens: 最大生成token数
            **kwargs: 其他API参数
            
        Returns:
            API返回的文本内容
            
        Raises:
            Exception: API调用失败时抛出异常
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 提取返回内容
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                raise ValueError("API返回结果为空")
                
        except Exception as e:
            raise Exception(f"DeepSeek API调用失败: {str(e)}")
    
    def simple_chat(self, user_message: str, system_message: Optional[str] = None) -> str:
        """
        简化的对话接口
        
        Args:
            user_message: 用户消息
            system_message: 系统消息（可选）
            
        Returns:
            AI回复内容
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": user_message})
        
        return self.chat_completion(messages)
    
    def review_with_prompt(
        self, 
        document_content: str, 
        review_prompt: str,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        使用指定提示词审查文档
        
        Args:
            document_content: 文档内容
            review_prompt: 审查提示词
            system_prompt: 系统提示词（可选）
            
        Returns:
            审查结果
        """
        # 默认系统提示词
        if not system_prompt:
            system_prompt = (
                "你是一个专业的专利审查助手，擅长分析专利申请文档。"
                "请基于用户的要求，对提供的专利文档进行专业、详细的审查分析。"
                "你的分析应该包括：问题识别、改进建议、法律风险提示等。"
                "请使用清晰、结构化的中文进行回答。"
            )
        
        # 组装用户消息
        user_message = f"""请根据以下要求审查这份专利申请文档：

审查要求：
{review_prompt}

专利文档内容：
{document_content}

请提供专业的审查意见。"""
        
        return self.simple_chat(user_message, system_prompt)
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接成功返回True，失败返回False
        """
        try:
            response = self.simple_chat("你好")
            return bool(response)
        except Exception:
            return False

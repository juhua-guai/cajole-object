# -*- coding: utf-8 -*-
"""LLM 服务模块"""

import json
import logging
from typing import TypedDict
from langchain_openai import ChatOpenAI

# 配置日志
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from src.config import Config, get_config
from src.prompts import SYSTEM_PROMPT, get_cold_start_prompt, get_time_period


class Suggestion(TypedDict):
    """建议选项"""
    label: str
    text: str


class LLMResponse(TypedDict):
    """LLM 响应"""
    reply: str
    suggestions: list[Suggestion]


class ConversationMemory:
    """对话记忆管理器（滑动窗口）"""
    
    def __init__(self, max_rounds: int = 10):
        self.max_rounds = max_rounds
        self.history: list[HumanMessage | AIMessage] = []
    
    def add_user_message(self, message: str):
        """添加用户消息"""
        self.history.append(HumanMessage(content=message))
        self._trim()
    
    def add_ai_message(self, message: str):
        """添加 AI 消息"""
        self.history.append(AIMessage(content=message))
        self._trim()
    
    def _trim(self):
        """裁剪历史，保留最近 N 轮"""
        max_messages = self.max_rounds * 2
        if len(self.history) > max_messages:
            self.history = self.history[-max_messages:]
    
    def get_messages(self) -> list:
        """获取所有消息"""
        return self.history.copy()
    
    def clear(self):
        """清空历史"""
        self.history.clear()


class LLMService:
    """LLM 服务类"""
    
    def __init__(self, config: Config | None = None):
        """初始化 LLM 服务
        
        Args:
            config: 配置对象，默认使用全局配置
        """
        self.config = config or get_config()
        self.llm = ChatOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
        )
        
        # 对话历史管理（滑动窗口）
        self.memory = ConversationMemory(max_rounds=self.config.max_history_rounds)
        
        # ChatPromptTemplate 模板
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # 构建链
        self.chain = self.prompt_template | self.llm
    
    def _invoke_model(self, history: list, user_message: str, current_mode: str):
        """调用模型，统一做异常处理"""
        try:
            return self.chain.invoke({
                "current_mode": self._get_mode_text(current_mode),
                "history": history,
                "input": user_message
            })
        except Exception as e:
            # 兼容部分代理在限流/欠费时返回非标准 OpenAI 响应，导致 choices 为空
            msg = str(e)
            if "429" in msg or "quota" in msg.lower():
                logger.error("LLM 请求命中额度/速率限制: %s", msg)
                raise RuntimeError(
                    "模型接口返回 429（额度/速率受限），请检查套餐、并发上限或更换可用的 key/model"
                ) from e
            if "null value for `choices`" in msg:
                logger.error("LLM 返回了空的 choices，可能是接口限流/余额不足或返回格式不兼容")
                raise RuntimeError(
                    "模型接口返回空响应（choices 为空），请检查额度/限速或确认当前接口代理是否兼容 OpenAI 协议"
                ) from e
            logger.exception("LLM 调用失败")
            raise
    
    def _parse_response(self, content: str) -> LLMResponse:
        """解析 LLM 响应
        
        Args:
            content: LLM 返回的内容
        """
        try:
            # 尝试提取 JSON
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            return LLMResponse(
                reply=data.get("reply", ""),
                suggestions=data.get("suggestions", [])
            )
        except json.JSONDecodeError:
            # 解析失败时返回默认响应
            return LLMResponse(
                reply=content if content else "本国宝的小笨脑袋出了点问题...",
                suggestions=[
                    {"label": "A", "text": "没关系，再说一遍嘛~"},
                    {"label": "B", "text": "嗯，好吧"},
                    {"label": "C", "text": "你是不是傻！"},
                ]
            )
    
    def _get_mode_text(self, current_mode: str) -> str:
        """获取模式描述文本"""
        if current_mode == "roast":
            return "作死模式 (Roast Mode) - 尽情阴阳怪气，调侃一二"
        return "求生模式 (Survival Mode) - 卑微认错，讨好一二"
    
    def generate_response(self, user_message: str, current_mode: str = "roast") -> LLMResponse:
        """生成回复
        
        Args:
            user_message: 用户消息
            current_mode: 当前模式，"roast" 或 "survival"
        
        Returns:
            LLMResponse: 包含 reply 和 suggestions 的响应
        """
        # 获取历史消息
        history = self.memory.get_messages()
        
        # 打印请求日志
        logger.info("=" * 50)
        logger.info("[LLM 请求] generate_response")
        logger.info(f"  用户输入: {user_message}")
        logger.info(f"  当前模式: {current_mode}")
        logger.info(f"  历史消息数: {len(history)}")
        for i, msg in enumerate(history):
            msg_type = "User" if isinstance(msg, HumanMessage) else "AI"
            logger.debug(f"    [{i}] {msg_type}: {msg.content[:50]}...")
        
        # 调用链
        response = self._invoke_model(history, user_message, current_mode)
        
        # 打印响应日志
        logger.info(f"[LLM 响应] {response.content}")
        logger.info("=" * 50)
        
        result = self._parse_response(response.content)
        
        # 保存到记忆
        self.memory.add_user_message(user_message)
        self.memory.add_ai_message(result["reply"])
        
        return result
    
    def generate_cold_start(self, current_mode: str = "roast") -> LLMResponse:
        """生成破冰消息
        
        Args:
            current_mode: 当前模式
        
        Returns:
            LLMResponse: 包含 reply 和 suggestions 的响应
        """
        time_period = get_time_period()
        cold_start_message = get_cold_start_prompt(time_period)
        
        # 打印请求日志
        logger.info("=" * 50)
        logger.info("[LLM 请求] generate_cold_start")
        logger.info(f"  破冰提示: {cold_start_message}")
        logger.info(f"  当前模式: {current_mode}")
        logger.info(f"  时间段: {time_period}")
        
        # 破冰消息使用空历史
        response = self._invoke_model([], cold_start_message, current_mode)
        
        # 打印响应日志
        logger.info(f"[LLM 响应] {response.content}")
        logger.info("=" * 50)
        
        result = self._parse_response(response.content)
        
        # 破冰消息只保存助手回复到记忆（作为对话开始）
        self.memory.add_ai_message(result["reply"])
        
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self.memory.clear()
    
    def get_history(self) -> list:
        """获取对话历史"""
        return self.memory.get_messages()

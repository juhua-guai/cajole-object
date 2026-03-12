# -*- coding: utf-8 -*-
"""聊天控制器 - 供 FastAPI 路由调用，无 PyQt 依赖"""

import asyncio
import re
from typing import Literal

from src.config import Config, get_config
from src.state_manager import StateManager, ModeType, ChoiceType
from src.llm_service import LLMService
from src.emotion_analyzer import EmotionAnalyzer


# 乱码兜底文案
FALLBACK_REPLIES = [
    "本国宝的小笨脑袋看不懂你在说什么...",
    "一二你是不是在说火星语？本国宝听不懂！",
    "这是什么神秘代码？本国宝表示困惑...",
    "小笨一二又在发奇怪的东西了！",
]

FALLBACK_SUGGESTIONS = [
    {"label": "A", "text": "哈哈，我重新说~"},
    {"label": "B", "text": "算了，没什么"},
    {"label": "C", "text": "你才乱码！"},
]


def _is_gibberish(text: str) -> bool:
    """检测是否为乱码文本"""
    if not text or len(text.strip()) == 0:
        return True
    # 过多特殊字符
    special_ratio = len(re.findall(r'[^\w\s\u4e00-\u9fff]', text)) / max(len(text), 1)
    if special_ratio > 0.5:
        return True
    # 过多连续相同字符
    if re.search(r'(.)\1{5,}', text):
        return True
    return False


class ChatController:
    """聊天控制器

    返回值约定：
    - 所有方法返回的 dict 包含 reply, suggestions 字段
    - 不包含 mode 字段，由路由层通过 get_current_mode() 补充
    - mode_changed 字段可选，仅在模式切换时存在
    """

    def __init__(self, config: Config | None = None):
        self.config = config or get_config()
        self.state = StateManager()
        self.llm_service = LLMService(self.config)
        self.emotion_analyzer = EmotionAnalyzer(self.config)

    # ========== 公开异步方法（供路由调用）==========

    async def start_cold_start(self) -> dict:
        """生成破冰消息（异步）"""
        return await asyncio.to_thread(self._do_cold_start)

    async def handle_suggestion_click(self, choice: ChoiceType, text: str) -> dict:
        """处理建议卡片点击（异步）"""
        return await asyncio.to_thread(self._do_suggestion_click, choice, text)

    async def handle_manual_input(self, text: str) -> dict:
        """处理手动输入（异步）"""
        return await asyncio.to_thread(self._do_manual_input, text)

    async def handle_mode_toggle(self) -> dict:
        """处理模式切换请求（异步）"""
        return await asyncio.to_thread(self._do_mode_toggle)

    # ========== 同步查询方法 ==========

    def get_current_mode(self) -> ModeType:
        """获取当前模式"""
        return self.state.current_mode

    def get_state(self) -> dict:
        """获取当前状态"""
        return {
            "mode": self.state.current_mode,
            "desired_mode": self.state.desired_mode,
            "happy_count": self.state.happy_choice_count,
            "angry_count": self.state.angry_choice_count,
        }

    def reset(self):
        """重置控制器状态"""
        self.state.reset()
        self.llm_service.clear_history()

    # ========== 内部同步实现 ==========

    def _do_cold_start(self) -> dict:
        """执行破冰消息生成"""
        response = self.llm_service.generate_cold_start(self.state.current_mode)
        self.state.add_assistant_message(response["reply"])
        return {"reply": response["reply"], "suggestions": response["suggestions"]}

    def _do_suggestion_click(self, choice: ChoiceType, text: str) -> dict:
        """执行建议卡片点击处理"""
        self.state.add_user_message(text, choice)
        mode_change = self.state.record_choice(choice)
        response = self.llm_service.generate_response(text, self.state.current_mode)
        self.state.add_assistant_message(response["reply"])

        result = {"reply": response["reply"], "suggestions": response["suggestions"]}
        if mode_change:
            result["mode_changed"] = mode_change
        return result

    def _do_manual_input(self, text: str) -> dict:
        """执行手动输入处理"""
        import random
        
        # 乱码检测兜底
        if _is_gibberish(text):
            reply = random.choice(FALLBACK_REPLIES)
            self.state.add_user_message(text, "B")
            self.state.add_assistant_message(reply)
            return {"reply": reply, "suggestions": FALLBACK_SUGGESTIONS}
        
        emotion_choice = self.emotion_analyzer.analyze(text)
        self.state.add_user_message(text, emotion_choice)
        mode_change = self.state.record_choice(emotion_choice)
        response = self.llm_service.generate_response(text, self.state.current_mode)
        self.state.add_assistant_message(response["reply"])

        result = {"reply": response["reply"], "suggestions": response["suggestions"]}
        if mode_change:
            result["mode_changed"] = mode_change
        return result

    def _do_mode_toggle(self) -> dict:
        """执行模式切换"""
        target_mode: ModeType = "survival" if self.state.current_mode == "roast" else "roast"
        result = self.state.request_mode_change(target_mode)
        return {
            "accepted": result.accepted,
            "current_mode": self.state.current_mode,
            "reason": result.reason,
        }

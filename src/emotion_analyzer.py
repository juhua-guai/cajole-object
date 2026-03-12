# -*- coding: utf-8 -*-
"""情绪分析模块"""

from typing import Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from src.config import Config, get_config
from src.prompts import get_emotion_analysis_prompt


EmotionType = Literal["A", "B", "C"]


# 情绪关键词词典
EMOTION_KEYWORDS = {
    "A": [  # 开心/撒娇/积极
        "哈哈", "嘿嘿", "嘻嘻", "开心", "高兴", "喜欢", "爱你", "好耶", "太棒了",
        "真好", "好呀", "好的呀", "可以呀", "没问题", "好哒", "好嘞", "么么哒",
        "亲亲", "抱抱", "撒娇", "人家", "嘛", "呀", "哼", "求求", "拜托",
    ],
    "B": [  # 平淡/中性
        "嗯", "哦", "好", "行", "可以", "知道了", "好吧", "行吧", "随便",
        "都行", "无所谓", "还好", "一般", "普通", "正常",
    ],
    "C": [  # 暴怒/拒绝/消极
        "滚", "走开", "烦", "讨厌", "生气", "愤怒", "不要", "不行", "拒绝",
        "闭嘴", "shut up", "去死", "傻", "笨", "蠢", "白痴", "混蛋", "可恶",
        "气死", "炸毛", "暴怒", "不理你", "哼", "切",
    ],
}


class EmotionAnalyzer:
    """情绪分析器"""
    
    def __init__(self, config: Config | None = None):
        """初始化情绪分析器
        
        Args:
            config: 配置对象，默认使用全局配置
        """
        self.config = config or get_config()
        self.client = ChatOpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
        )
        # 关键词快速检测阈值
        self.keyword_check_enabled = True
        self.llm_analysis_threshold = 10  # 文本长度阈值
        self.fallback_emotion = "B"  # 默认情绪
    
    def _keyword_check(self, text: str) -> EmotionType | None:
        """关键词快速检测
        
        Args:
            text: 用户输入文本
        
        Returns:
            检测到的情绪类型，未检测到返回 None
        """
        text_lower = text.lower()
        
        # 按优先级检测：C > A > B（暴怒优先）
        for keyword in EMOTION_KEYWORDS["C"]:
            if keyword in text_lower:
                return "C"
        
        for keyword in EMOTION_KEYWORDS["A"]:
            if keyword in text_lower:
                return "A"
        
        for keyword in EMOTION_KEYWORDS["B"]:
            if keyword in text_lower:
                return "B"
        
        return None
    
    def _llm_analyze(self, text: str) -> EmotionType:
        """使用 LLM 进行情绪分析
        
        Args:
            text: 用户输入文本
        
        Returns:
            情绪类型
        """
        try:
            prompt = get_emotion_analysis_prompt(text)
            messages = [HumanMessage(content=prompt)]
            response = self.client.invoke(messages)
            
            result = response.content.strip().upper()
            if result in ["A", "B", "C"]:
                return result
            
            # 尝试从响应中提取
            for char in ["A", "B", "C"]:
                if char in result:
                    return char
            
            return self.fallback_emotion
        except Exception:
            return self.fallback_emotion
    
    def analyze(self, text: str) -> EmotionType:
        """分析用户输入的情绪
        
        Args:
            text: 用户输入文本
        
        Returns:
            情绪类型: "A" (开心), "B" (平淡), "C" (暴怒)
        """
        if not text or not text.strip():
            return self.fallback_emotion
        
        # 1. 尝试关键词快速检测
        if self.keyword_check_enabled:
            keyword_result = self._keyword_check(text)
            if keyword_result:
                return keyword_result
        
        # 2. 短文本直接返回默认
        if len(text) < self.llm_analysis_threshold:
            return self.fallback_emotion
        
        # 3. 使用 LLM 分析
        return self._llm_analyze(text)
    
    def emotion_to_label(self, emotion: EmotionType) -> str:
        """将情绪类型转换为标签描述
        
        Args:
            emotion: 情绪类型
        
        Returns:
            标签描述
        """
        labels = {
            "A": "开心/撒娇",
            "B": "平淡/中性",
            "C": "暴怒/拒绝",
        }
        return labels.get(emotion, "未知")

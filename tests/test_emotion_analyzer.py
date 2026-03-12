# -*- coding: utf-8 -*-
"""情绪分析模块测试"""

import pytest
from src.emotion_analyzer import EmotionAnalyzer, EMOTION_KEYWORDS


class TestEmotionAnalyzerUnit:
    """情绪分析器单元测试"""
    
    def test_keyword_check_happy(self):
        """测试开心关键词检测"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        analyzer.keyword_check_enabled = True
        
        assert analyzer._keyword_check("哈哈好开心") == "A"
        assert analyzer._keyword_check("嘿嘿") == "A"
        assert analyzer._keyword_check("爱你呀") == "A"
    
    def test_keyword_check_neutral(self):
        """测试平淡关键词检测"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        analyzer.keyword_check_enabled = True
        
        assert analyzer._keyword_check("嗯") == "B"
        assert analyzer._keyword_check("好吧") == "B"
        assert analyzer._keyword_check("知道了") == "B"
    
    def test_keyword_check_furious(self):
        """测试暴怒关键词检测"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        analyzer.keyword_check_enabled = True
        
        assert analyzer._keyword_check("滚开") == "C"
        assert analyzer._keyword_check("气死我了") == "C"
        assert analyzer._keyword_check("讨厌你") == "C"
    
    def test_keyword_check_priority(self):
        """测试暴怒优先级"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        analyzer.keyword_check_enabled = True
        
        # 同时包含开心和暴怒关键词时，暴怒优先
        assert analyzer._keyword_check("哈哈你去死吧") == "C"
    
    def test_keyword_check_no_match(self):
        """测试无匹配关键词"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        analyzer.keyword_check_enabled = True
        
        assert analyzer._keyword_check("今天天气不错") is None
    
    def test_emotion_to_label(self):
        """测试情绪标签转换"""
        from src.config import Config
        
        analyzer = EmotionAnalyzer.__new__(EmotionAnalyzer)
        
        assert "开心" in analyzer.emotion_to_label("A")
        assert "平淡" in analyzer.emotion_to_label("B")
        assert "暴怒" in analyzer.emotion_to_label("C")


class TestEmotionAnalyzerIntegration:
    """情绪分析器集成测试"""
    
    @pytest.mark.integration
    def test_analyze_with_llm(self):
        """测试 LLM 情绪分析"""
        analyzer = EmotionAnalyzer()
        
        # 测试明显的情绪
        result = analyzer.analyze("我今天心情特别好，想和你一起去吃火锅庆祝一下")
        print(f"\n输入: 我今天心情特别好... -> 情绪: {result}")
        assert result in ["A", "B", "C"]
        
        result = analyzer.analyze("我非常生气，你总是不听我说话，我再也不想理你了")
        print(f"输入: 我非常生气... -> 情绪: {result}")
        assert result in ["A", "B", "C"]

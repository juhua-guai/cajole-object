# -*- coding: utf-8 -*-
"""Prompt 模板模块测试"""

import pytest
from src.prompts import (
    get_system_prompt,
    get_cold_start_prompt,
    get_emotion_analysis_prompt,
    get_time_period,
)


class TestPrompts:
    """测试 Prompt 模板"""
    
    def test_get_system_prompt_roast_mode(self):
        """测试作死模式系统提示词"""
        prompt = get_system_prompt("roast")
        
        assert "布布" in prompt
        assert "一二" in prompt
        assert "本国宝" in prompt
        assert "熊底捞" in prompt
        assert "小笨" in prompt
        assert "作死模式" in prompt
        assert "JSON" in prompt
    
    def test_get_system_prompt_survival_mode(self):
        """测试求生模式系统提示词"""
        prompt = get_system_prompt("survival")
        
        assert "求生模式" in prompt
        assert "卑微认错" in prompt
    
    def test_get_cold_start_prompt(self):
        """测试破冰消息提示词"""
        prompt = get_cold_start_prompt("中午")
        
        assert "中午" in prompt
        assert "贪吃" in prompt
    
    def test_get_emotion_analysis_prompt(self):
        """测试情绪分析提示词"""
        prompt = get_emotion_analysis_prompt("我好开心呀")
        
        assert "我好开心呀" in prompt
        assert "A" in prompt
        assert "B" in prompt
        assert "C" in prompt
    
    def test_get_time_period(self):
        """测试时间段获取"""
        period = get_time_period()
        
        valid_periods = ["早上", "上午", "中午", "下午", "傍晚", "晚上", "深夜"]
        assert period in valid_periods

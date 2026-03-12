# -*- coding: utf-8 -*-
"""聊天控制器模块测试"""

import pytest
from unittest.mock import MagicMock, patch

from src.state_manager import StateManager
from src.config import Config


class TestChatControllerLogic:
    """聊天控制器逻辑测试（不使用 Qt）"""
    
    def test_state_integration_with_controller_logic(self):
        """测试状态管理与控制器逻辑集成"""
        state = StateManager()
        
        # 模拟连续 3 次 C
        state.record_choice("C")
        state.record_choice("C")
        result = state.record_choice("C")
        
        assert result == "to_survival"
        assert state.current_mode == "survival"
    
    def test_mode_toggle_logic(self):
        """测试模式切换逻辑"""
        state = StateManager()
        
        assert state.current_mode == "roast"
        
        state.toggle_mode()
        assert state.current_mode == "survival"
        
        state.toggle_mode()
        assert state.current_mode == "roast"
    
    def test_emotion_to_choice_flow(self):
        """测试情绪到选项的流程"""
        # 模拟情绪分析器返回值
        emotion_choices = ["A", "B", "C"]
        
        for choice in emotion_choices:
            state = StateManager()
            result = state.record_choice(choice)
            
            if choice == "C":
                assert state.angry_choice_count == 1
            else:
                assert state.angry_choice_count == 0
    
    def test_survival_mode_exit_flow(self):
        """测试求生模式退出流程"""
        state = StateManager()
        state.set_mode("survival")
        
        # 连续 3 次 A 应该退出求生模式
        state.record_choice("A")
        state.record_choice("A")
        result = state.record_choice("A")
        
        assert result == "to_roast"
        assert state.current_mode == "roast"
    
    def test_reset_clears_all(self):
        """测试重置清除所有状态"""
        state = StateManager()
        state.set_mode("survival")
        state.happy_choice_count = 2
        state.angry_choice_count = 1
        
        state.reset()
        
        assert state.current_mode == "roast"
        assert state.happy_choice_count == 0
        assert state.angry_choice_count == 0


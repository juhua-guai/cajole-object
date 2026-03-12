# -*- coding: utf-8 -*-
"""状态管理模块测试"""

import pytest
from src.state_manager import StateManager


class TestStateManager:
    """状态管理器测试"""
    
    def test_initial_state(self):
        """测试初始状态"""
        manager = StateManager()
        
        assert manager.current_mode == "roast"
        assert manager.happy_choice_count == 0
        assert manager.angry_choice_count == 0
    
    def test_roast_mode_single_c(self):
        """测试作死模式下单次选择 C"""
        manager = StateManager()
        
        result = manager.record_choice("C")
        
        assert result is None
        assert manager.current_mode == "roast"
        assert manager.angry_choice_count == 1
    
    def test_roast_mode_three_c_triggers_survival(self):
        """测试作死模式下连续 3 次 C 进入求生模式"""
        manager = StateManager()
        
        manager.record_choice("C")
        manager.record_choice("C")
        result = manager.record_choice("C")
        
        assert result == "to_survival"
        assert manager.current_mode == "survival"
        assert manager.angry_choice_count == 0
    
    def test_roast_mode_a_resets_counter(self):
        """测试作死模式下选择 A 重置计数器"""
        manager = StateManager()
        
        manager.record_choice("C")
        manager.record_choice("C")
        manager.record_choice("A")  # 重置
        
        assert manager.angry_choice_count == 0
        assert manager.current_mode == "roast"
    
    def test_roast_mode_b_resets_counter(self):
        """测试作死模式下选择 B 重置计数器"""
        manager = StateManager()
        
        manager.record_choice("C")
        manager.record_choice("B")  # 重置
        
        assert manager.angry_choice_count == 0
    
    def test_survival_mode_single_a(self):
        """测试求生模式下单次选择 A"""
        manager = StateManager()
        manager.set_mode("survival")
        
        result = manager.record_choice("A")
        
        assert result is None
        assert manager.current_mode == "survival"
        assert manager.happy_choice_count == 1
    
    def test_survival_mode_three_a_triggers_roast(self):
        """测试求生模式下连续 3 次 A 恢复作死模式"""
        manager = StateManager()
        manager.set_mode("survival")
        
        manager.record_choice("A")
        manager.record_choice("A")
        result = manager.record_choice("A")
        
        assert result == "to_roast"
        assert manager.current_mode == "roast"
        assert manager.happy_choice_count == 0
    
    def test_survival_mode_b_resets_counter(self):
        """测试求生模式下选择 B 重置计数器"""
        manager = StateManager()
        manager.set_mode("survival")
        
        manager.record_choice("A")
        manager.record_choice("A")
        manager.record_choice("B")  # 重置
        
        assert manager.happy_choice_count == 0
        assert manager.current_mode == "survival"
    
    def test_survival_mode_c_resets_counter(self):
        """测试求生模式下选择 C 重置计数器"""
        manager = StateManager()
        manager.set_mode("survival")
        
        manager.record_choice("A")
        manager.record_choice("C")  # 重置
        
        assert manager.happy_choice_count == 0
    
    def test_toggle_mode(self):
        """测试手动切换模式"""
        manager = StateManager()
        
        assert manager.current_mode == "roast"
        
        result = manager.toggle_mode()
        assert result == "survival"
        assert manager.current_mode == "survival"
        
        result = manager.toggle_mode()
        assert result == "roast"
        assert manager.current_mode == "roast"
    
    def test_toggle_resets_counters(self):
        """测试手动切换重置计数器"""
        manager = StateManager()
        
        manager.record_choice("C")
        manager.record_choice("C")
        assert manager.angry_choice_count == 2
        
        manager.toggle_mode()
        
        assert manager.angry_choice_count == 0
        assert manager.happy_choice_count == 0
    
    def test_reset(self):
        """测试重置状态"""
        manager = StateManager()
        manager.set_mode("survival")
        manager.happy_choice_count = 2
        manager.add_user_message("测试", "A")
        
        manager.reset()
        
        assert manager.current_mode == "roast"
        assert manager.happy_choice_count == 0
        assert manager.angry_choice_count == 0
        assert len(manager.conversation_history) == 0
    
    def test_conversation_history(self):
        """测试对话历史管理"""
        manager = StateManager()
        
        manager.add_user_message("你好", "A")
        manager.add_assistant_message("你好呀小笨熊")
        
        history = manager.get_conversation_history()
        assert len(history) == 2
        assert history[0].role == "user"
        assert history[0].content == "你好"
        assert history[0].choice == "A"
        assert history[1].role == "assistant"
        assert history[1].content == "你好呀小笨熊"
    
    def test_clear_conversation_history(self):
        """测试清空对话历史"""
        manager = StateManager()
        manager.add_user_message("测试", "B")
        manager.add_assistant_message("回复")
        
        manager.clear_conversation_history()
        
        assert len(manager.conversation_history) == 0

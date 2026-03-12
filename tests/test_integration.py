# -*- coding: utf-8 -*-
"""集成测试 - 完整流程验证"""

import pytest
from src.llm_service import LLMService
from src.emotion_analyzer import EmotionAnalyzer
from src.state_manager import StateManager


class TestIntegrationFlows:
    """集成测试 - 验证完整流程"""
    
    @pytest.mark.integration
    def test_cold_start_flow(self):
        """测试破冰消息完整流程"""
        service = LLMService()
        state = StateManager()
        
        # 生成破冰消息
        response = service.generate_cold_start("roast")
        
        # 验证响应格式
        assert "reply" in response
        assert "suggestions" in response
        assert len(response["reply"]) > 0
        assert len(response["suggestions"]) == 3
        
        # 验证建议选项格式
        for suggestion in response["suggestions"]:
            assert "label" in suggestion
            assert "text" in suggestion
            assert suggestion["label"] in ["A", "B", "C"]
        
        # 记录到状态
        state.add_assistant_message(response["reply"])
        assert len(state.conversation_history) == 1
        
        print(f"\n[破冰消息] {response['reply']}")
    
    @pytest.mark.integration
    def test_suggestion_click_flow(self):
        """测试建议卡片点击完整流程"""
        service = LLMService()
        state = StateManager()
        
        # 先获取破冰消息
        cold_start = service.generate_cold_start("roast")
        state.add_assistant_message(cold_start["reply"])
        
        # 模拟点击 A 选项
        suggestion_text = cold_start["suggestions"][0]["text"]
        state.add_user_message(suggestion_text, "A")
        state.record_choice("A")
        
        # 生成回复
        response = service.generate_response(suggestion_text, state.current_mode)
        state.add_assistant_message(response["reply"])
        
        # 验证
        assert len(state.conversation_history) == 3  # 1 AI + 1 User + 1 AI
        assert state.current_mode == "roast"  # 单次 A 不切换模式
        
        print(f"\n[用户选择A] {suggestion_text}")
        print(f"[布布回复] {response['reply']}")
    
    @pytest.mark.integration
    def test_mode_switch_flow(self):
        """测试模式切换完整流程 - 连续3次C进入求生模式"""
        service = LLMService()
        state = StateManager()
        
        # 初始状态
        assert state.current_mode == "roast"
        
        # 模拟连续 3 次选择 C
        for i in range(3):
            response = service.generate_response(f"滚开！不想理你！第{i+1}次", state.current_mode)
            state.add_user_message(f"滚开！不想理你！第{i+1}次", "C")
            mode_change = state.record_choice("C")
            state.add_assistant_message(response["reply"])
            
            print(f"\n[第{i+1}次选C] 模式: {state.current_mode}")
            print(f"[布布回复] {response['reply'][:50]}...")
            
            if mode_change == "to_survival":
                break
        
        # 验证进入求生模式
        assert state.current_mode == "survival"
        
        # 求生模式下的回复应该更卑微
        response = service.generate_response("哼！", "survival")
        print(f"\n[求生模式回复] {response['reply']}")
    
    @pytest.mark.integration
    def test_manual_input_emotion_analysis_flow(self):
        """测试手动输入情绪分析完整流程"""
        analyzer = EmotionAnalyzer()
        state = StateManager()
        service = LLMService()
        
        # 测试开心情绪
        happy_text = "哈哈哈，太开心了，我们去吃火锅吧！"
        emotion = analyzer.analyze(happy_text)
        print(f"\n[情绪分析] '{happy_text}' -> {emotion}")
        assert emotion in ["A", "B", "C"]
        
        # 测试暴怒情绪
        angry_text = "气死我了！你这个笨蛋！滚开！"
        emotion = analyzer.analyze(angry_text)
        print(f"[情绪分析] '{angry_text}' -> {emotion}")
        assert emotion == "C"  # 应该识别为暴怒
        
        # 完整流程：分析情绪 -> 记录选择 -> 生成回复
        state.add_user_message(angry_text, emotion)
        state.record_choice(emotion)
        response = service.generate_response(angry_text, state.current_mode)
        state.add_assistant_message(response["reply"])
        
        print(f"[布布回复] {response['reply']}")
        assert len(state.conversation_history) == 2
    
    @pytest.mark.integration
    def test_conversation_history_persistence(self):
        """测试对话历史持久化"""
        service = LLMService()
        state = StateManager()
        
        # 多轮对话
        messages = ["你好", "我饿了", "想吃火锅"]
        
        for msg in messages:
            state.add_user_message(msg, "B")
            response = service.generate_response(msg, state.current_mode)
            state.add_assistant_message(response["reply"])
        
        # 验证历史
        history = state.get_conversation_history()
        assert len(history) == 6  # 3 user + 3 assistant
        
        # 验证顺序
        assert history[0].role == "user"
        assert history[0].content == "你好"
        assert history[1].role == "assistant"
        
        print(f"\n[对话历史] 共 {len(history)} 条消息")
        for h in history:
            print(f"  [{h.role}] {h.content[:30]}...")
        
        # 重置
        state.reset()
        assert len(state.conversation_history) == 0

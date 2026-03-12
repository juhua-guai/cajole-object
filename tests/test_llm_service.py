# -*- coding: utf-8 -*-
"""LLM 服务模块测试"""

import pytest
from src.llm_service import LLMService, LLMResponse


class TestLLMServiceUnit:
    """LLM 服务单元测试（不调用API）"""
    
    def test_parse_response_valid_json(self):
        """测试有效 JSON 解析"""
        from src.config import Config
        
        # 创建部分初始化的服务对象
        service = LLMService.__new__(LLMService)
        service.config = Config(api_key="test", model_name="test")
        
        content = '''{"reply": "你好啊小笨熊", "suggestions": [{"label": "A", "text": "嘿嘿"}, {"label": "B", "text": "嗯"}, {"label": "C", "text": "滚"}]}'''
        result = service._parse_response(content)
        
        assert result["reply"] == "你好啊小笨熊"
        assert len(result["suggestions"]) == 3
        assert result["suggestions"][0]["label"] == "A"
    
    def test_parse_response_with_markdown(self):
        """测试带 markdown 代码块的 JSON 解析"""
        from src.config import Config
        
        service = LLMService.__new__(LLMService)
        service.config = Config(api_key="test", model_name="test")
        
        content = '''```json
{"reply": "本国宝来了", "suggestions": [{"label": "A", "text": "好耶"}, {"label": "B", "text": "哦"}, {"label": "C", "text": "走开"}]}
```'''
        result = service._parse_response(content)
        
        assert result["reply"] == "本国宝来了"
        assert len(result["suggestions"]) == 3
    
    def test_parse_response_invalid_json(self):
        """测试无效 JSON 返回默认响应"""
        from src.config import Config
        
        service = LLMService.__new__(LLMService)
        service.config = Config(api_key="test", model_name="test")
        
        content = "这不是JSON格式"
        result = service._parse_response(content)
        
        assert "这不是JSON格式" in result["reply"]
        assert len(result["suggestions"]) == 3
    
    def test_get_mode_text(self):
        """测试模式文本获取"""
        from src.config import Config
        
        service = LLMService.__new__(LLMService)
        service.config = Config(api_key="test", model_name="test")
        
        roast_text = service._get_mode_text("roast")
        assert "作死模式" in roast_text
        
        survival_text = service._get_mode_text("survival")
        assert "求生模式" in survival_text


class TestLLMServiceIntegration:
    """LLM 服务集成测试（需要 API）"""
    
    @pytest.mark.integration
    def test_generate_cold_start(self):
        """测试破冰消息生成"""
        service = LLMService()
        result = service.generate_cold_start("roast")
        
        assert "reply" in result
        assert "suggestions" in result
        assert len(result["reply"]) > 0
        assert len(result["suggestions"]) == 3
        print(f"\n破冰消息: {result['reply']}")
        for s in result["suggestions"]:
            print(f"  [{s['label']}] {s['text']}")
    
    @pytest.mark.integration
    def test_generate_response(self):
        """测试对话回复生成"""
        service = LLMService()
        result = service.generate_response("我饿了", "roast")
        
        assert "reply" in result
        assert "suggestions" in result
        assert len(result["reply"]) > 0
        print(f"\n布布回复: {result['reply']}")
        for s in result["suggestions"]:
            print(f"  [{s['label']}] {s['text']}")
    
    @pytest.mark.integration
    def test_memory_works(self):
        """测试对话记忆功能"""
        service = LLMService()
        
        # 第一轮对话
        service.generate_response("我叫小白", "roast")
        
        # 检查历史
        history = service.get_history()
        assert len(history) == 2  # 一条用户消息 + 一条 AI 消息
        
        # 清空历史
        service.clear_history()
        history = service.get_history()
        assert len(history) == 0

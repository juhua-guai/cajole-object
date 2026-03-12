# -*- coding: utf-8 -*-
"""配置模块测试"""

import pytest
from pathlib import Path


class TestConfig:
    """测试配置模块"""
    
    def test_load_config_missing_file(self):
        """测试配置文件不存在时抛出异常"""
        import src.config as config_module
        config_module.reset_config()
        
        with pytest.raises(ValueError, match="配置文件不存在"):
            config_module.load_config(Path("/nonexistent/config.toml"))
    
    def test_load_config_missing_api_key(self, tmp_path):
        """测试缺少 API Key 时抛出异常"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[api]
api_key = "your_api_key_here"
""")
        
        import src.config as config_module
        config_module.reset_config()
        
        with pytest.raises(ValueError, match="CAJOLE_API_KEY"):
            config_module.load_config(config_file)
    
    def test_load_config_with_api_key(self, tmp_path):
        """测试有 API Key 时正常加载"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[api]
api_key = "test_key_123"
model_name = "openai/gpt-4o"

[chat]
max_history_rounds = 15
""")
        
        import src.config as config_module
        config_module.reset_config()
        
        config = config_module.load_config(config_file)
        
        assert config.api_key == "test_key_123"
        assert config.model_name == "openai/gpt-4o"
        assert config.max_history_rounds == 15

    def test_load_config_from_env_when_default_file_missing(self, tmp_path, monkeypatch):
        """测试默认配置文件缺失时可从环境变量加载"""
        import src.config as config_module

        monkeypatch.setattr(config_module, "CONFIG_FILE", tmp_path / "missing.toml")
        monkeypatch.setenv(config_module.ENV_API_KEY, "env_key_123")
        monkeypatch.setenv(config_module.ENV_MODEL_NAME, "test-model")
        monkeypatch.setenv(config_module.ENV_MAX_HISTORY_ROUNDS, "22")
        config_module.reset_config()

        config = config_module.load_config()

        assert config.api_key == "env_key_123"
        assert config.base_url == config_module.DEFAULT_BASE_URL
        assert config.model_name == "test-model"
        assert config.max_history_rounds == 22

    def test_env_overrides_file_values(self, tmp_path, monkeypatch):
        """测试环境变量优先于文件配置"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[api]
api_key = "file_key"
model_name = "file-model"

[chat]
max_history_rounds = 5
""")

        import src.config as config_module

        monkeypatch.setenv(config_module.ENV_API_KEY, "env_key")
        monkeypatch.setenv(config_module.ENV_MODEL_NAME, "env-model")
        monkeypatch.setenv(config_module.ENV_MAX_HISTORY_ROUNDS, "9")
        config_module.reset_config()

        config = config_module.load_config(config_file)

        assert config.api_key == "env_key"
        assert config.base_url == config_module.DEFAULT_BASE_URL
        assert config.model_name == "env-model"
        assert config.max_history_rounds == 9
    
    def test_config_default_paths(self, tmp_path):
        """测试默认路径设置"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[api]
api_key = "test_key"
""")
        
        import src.config as config_module
        config_module.reset_config()
        
        config = config_module.load_config(config_file)
        
        assert "avatars" in str(config.bubu_avatar_path)
        assert config.bubu_avatar_path.name in {"bubu_avatar.png", "bubu_avatar.jpg"}
    
    def test_get_emotion_icon_path(self, tmp_path):
        """测试情绪图标路径获取"""
        config_file = tmp_path / "config.toml"
        config_file.write_text("""
[api]
api_key = "test_key"
""")
        
        import src.config as config_module
        config_module.reset_config()
        
        config = config_module.load_config(config_file)
        
        happy_path = config.get_emotion_icon_path("happy")
        assert "icon_happy.png" in str(happy_path)
        
        neutral_path = config.get_emotion_icon_path("neutral")
        assert "icon_neutral.png" in str(neutral_path)

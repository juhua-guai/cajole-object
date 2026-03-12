# -*- coding: utf-8 -*-
"""配置管理模块"""

import os
import tomllib
from pathlib import Path
from dataclasses import dataclass, field


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.toml"
EXAMPLE_CONFIG_FILE = PROJECT_ROOT / "config.example.toml"

DEFAULT_MODEL_NAME = "openai/gpt-4o"
DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MAX_HISTORY_ROUNDS = 10

ENV_API_KEY = "CAJOLE_API_KEY"
ENV_MODEL_NAME = "CAJOLE_MODEL_NAME"
ENV_MAX_HISTORY_ROUNDS = "CAJOLE_MAX_HISTORY_ROUNDS"


@dataclass
class Config:
    """应用配置类"""
    
    # API 配置
    api_key: str = ""
    model_name: str = DEFAULT_MODEL_NAME
    base_url: str = DEFAULT_BASE_URL
    
    # 对话配置
    max_history_rounds: int = DEFAULT_MAX_HISTORY_ROUNDS
    
    # 资源路径
    assets_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "assets")
    bubu_avatar_path: Path | None = None
    bubu_scared_path: Path | None = None
    yier_avatar_path: Path | None = None
    
    def __post_init__(self):
        """初始化后设置默认路径"""
        def _prefer_jpg_if_png_missing(default_png: Path) -> Path:
            """默认使用 png，但若 png 不存在而同名 jpg 存在，自动切换到 jpg"""
            if default_png.exists():
                return default_png
            alt = default_png.with_suffix(".jpg")
            return alt if alt.exists() else default_png
        
        if self.bubu_avatar_path is None:
            self.bubu_avatar_path = _prefer_jpg_if_png_missing(self.assets_dir / "avatars" / "bubu_avatar.png")
        if self.bubu_scared_path is None:
            self.bubu_scared_path = _prefer_jpg_if_png_missing(self.assets_dir / "avatars" / "bubu_scared.png")
        if self.yier_avatar_path is None:
            self.yier_avatar_path = _prefer_jpg_if_png_missing(self.assets_dir / "avatars" / "yier_avatar.png")
    
    @property
    def placeholder_avatar_path(self) -> Path:
        return self.assets_dir / "placeholder" / "default_avatar.png"
    
    @property
    def broken_image_path(self) -> Path:
        return self.assets_dir / "placeholder" / "broken_image.png"
    
    def get_emotion_icon_path(self, emotion: str) -> Path:
        """获取情绪图标路径"""
        icon_map = {
            "happy": "icon_happy.png",
            "neutral": "icon_neutral.png",
            "furious": "icon_furious.png",
        }
        filename = icon_map.get(emotion, "icon_neutral.png")
        return self.assets_dir / "icons" / filename
    
    def to_dict(self) -> dict:
        """转换为字典（用于设置对话框）"""
        return {
            "api_key": self.api_key,
            "model_name": self.model_name,
        }
    
    def update_api_config(self, api_key: str, model_name: str):
        """更新 API 配置"""
        self.api_key = api_key
        self.model_name = model_name


def _load_toml_config(config_path: Path) -> dict:
    """读取 TOML 配置文件，不存在时返回空字典。"""
    if not config_path.exists():
        return {}

    with open(config_path, "rb") as f:
        return tomllib.load(f)


def _load_env_config() -> dict[str, str]:
    """读取环境变量配置。"""
    return {
        "api_key": os.getenv(ENV_API_KEY, "").strip(),
        "model_name": os.getenv(ENV_MODEL_NAME, "").strip(),
        "max_history_rounds": os.getenv(ENV_MAX_HISTORY_ROUNDS, "").strip(),
    }


def _parse_history_rounds(raw_value: object, default: int) -> int:
    """解析对话轮数配置，非法值时回退到默认值。"""
    if isinstance(raw_value, int):
        return raw_value

    if isinstance(raw_value, str):
        value = raw_value.strip()
        if value.isdigit():
            return int(value)

    return default


def load_config(config_path: Path | None = None) -> Config:
    """从配置文件加载配置
    
    Args:
        config_path: 配置文件路径，默认为项目根目录下的 config.toml
    """
    if config_path is None:
        config_path = CONFIG_FILE
    
    if config_path != CONFIG_FILE and not config_path.exists():
        raise ValueError(
            f"配置文件不存在: {config_path}\n"
            f"请复制 config.example.toml 为 config.toml 并填写配置"
        )
    
    data = _load_toml_config(config_path)
    env_config = _load_env_config()
    
    # 读取 API 配置
    api_section = data.get("api", {})
    api_key = env_config["api_key"] or api_section.get("api_key", "")
    
    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "缺少必填配置: 请复制 "
            f"{EXAMPLE_CONFIG_FILE.name} 为 {CONFIG_FILE.name} 并填写 api_key，"
            f"或设置环境变量 {ENV_API_KEY}"
        )
    
    model_name = env_config["model_name"] or api_section.get("model_name", DEFAULT_MODEL_NAME)
    
    # 读取对话配置
    chat_section = data.get("chat", {})
    max_history_rounds = _parse_history_rounds(
        env_config["max_history_rounds"] or chat_section.get("max_history_rounds", DEFAULT_MAX_HISTORY_ROUNDS),
        DEFAULT_MAX_HISTORY_ROUNDS,
    )
    
    config = Config(
        api_key=api_key,
        model_name=model_name,
        max_history_rounds=max_history_rounds,
    )
    
    # 读取资源路径配置
    assets_section = data.get("assets", {})
    if bubu_path := assets_section.get("bubu_avatar_path"):
        config.bubu_avatar_path = Path(bubu_path)
    if bubu_scared := assets_section.get("bubu_scared_path"):
        config.bubu_scared_path = Path(bubu_scared)
    if yier_path := assets_section.get("yier_avatar_path"):
        config.yier_avatar_path = Path(yier_path)
    
    return config


# 全局配置实例（延迟加载）
_config: Config | None = None


def get_config() -> Config:
    """获取全局配置实例"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reset_config() -> None:
    """重置全局配置（用于测试）"""
    global _config
    _config = None


def has_server_config(config_path: Path | None = None) -> bool:
    """判断后端是否已经具备可用配置。"""
    try:
        load_config(config_path)
    except ValueError:
        return False
    return True


def save_config(config: Config, config_path: Path | None = None) -> None:
    """保存配置到文件
    
    Args:
        config: 配置对象
        config_path: 配置文件路径，默认为项目根目录下的 config.toml
    """
    if config_path is None:
        config_path = CONFIG_FILE
    
    # 读取现有配置文件内容（保留注释和其他配置）
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    else:
        lines = []
    
    # 构建新的配置内容
    new_content = _update_config_content(lines, config)
    
    # 写入文件
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(new_content)


def _update_config_content(lines: list[str], config: Config) -> str:
    """更新配置文件内容，保留注释
    
    Args:
        lines: 原文件行列表
        config: 新配置对象
    
    Returns:
        更新后的文件内容
    """
    if not lines:
        # 创建新的配置文件
        return f'''# 应用配置文件

[api]
# 密钥（必填）
api_key = "{config.api_key}"
# 模型名称
model_name = "{config.model_name}"

[chat]
# 保留的最近对话轮数
max_history_rounds = {config.max_history_rounds}

[assets]
# 头像路径配置（可选，留空使用默认路径）
# bubu_avatar_path = "assets/avatars/bubu_avatar.png"
# bubu_scared_path = "assets/avatars/bubu_scared.png"
# yier_avatar_path = "assets/avatars/yier_avatar.png"
'''
    
    # 更新现有配置文件
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 检查是否是需要更新的配置项
        if stripped.startswith("api_key") and "=" in stripped:
            # 保留缩进
            indent = line[:len(line) - len(line.lstrip())]
            result.append(f'{indent}api_key = "{config.api_key}"\n')
        elif stripped.startswith("base_url") and "=" in stripped:
            pass
        elif stripped.startswith("model_name") and "=" in stripped:
            indent = line[:len(line) - len(line.lstrip())]
            result.append(f'{indent}model_name = "{config.model_name}"\n')
        else:
            result.append(line)
        
        i += 1
    
    return "".join(result)

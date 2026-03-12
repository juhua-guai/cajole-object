# -*- coding: utf-8 -*-
"""聊天相关 API 路由"""

from typing import Literal, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.config import Config, DEFAULT_MODEL_NAME, ENV_API_KEY, get_config
from src.chat_controller import ChatController

router = APIRouter()

_controller: ChatController | None = None


class ConfigRequest(BaseModel):
    """配置请求基类"""
    api_key: str | None = None
    model: str | None = None


class ColdStartRequest(ConfigRequest):
    """冷启动请求"""
    pass


class ReplyRequest(ConfigRequest):
    """回复请求"""
    text: str
    choice: Optional[Literal["A", "B", "C"]] = None


class ModeToggleRequest(BaseModel):
    """模式切换请求"""
    target_mode: Literal["roast", "survival"]


class SuggestionItem(BaseModel):
    """建议项"""
    label: str
    text: str


class ChatResponse(BaseModel):
    """聊天响应"""
    reply: str
    suggestions: list[SuggestionItem]
    current_mode: Literal["roast", "survival"]
    mode_changed: Optional[str] = None


class ModeToggleResponse(BaseModel):
    """模式切换响应"""
    accepted: bool
    current_mode: Literal["roast", "survival"]
    reason: Literal["already_in_mode", "pending_emotion_confirm", "emotion_supported"]


def _resolve_runtime_config(api_key: str | None, model: str | None) -> Config:
    """优先使用请求配置；未提供时回退到服务端配置。"""
    normalized_key = (api_key or "").strip()
    if normalized_key:
        return Config(
            api_key=normalized_key,
            model_name=(model or DEFAULT_MODEL_NAME).strip() or DEFAULT_MODEL_NAME,
        )

    try:
        return get_config()
    except ValueError as exc:
        raise ValueError(
            "当前后端未配置服务端模型凭据；请设置环境变量 "
            f"{ENV_API_KEY}，或在前端设置里输入临时 API Key。"
        ) from exc


def _get_controller(config: Config) -> ChatController:
    """获取或创建控制器（单用户演示版，配置变更时重建）"""
    global _controller
    
    if _controller is None:
        _controller = ChatController(config)
    else:
        current_config = _controller.config
        if (
            current_config.api_key != config.api_key
            or current_config.model_name != config.model_name
        ):
            _controller = ChatController(config)
    
    return _controller


@router.post("/cold-start", response_model=ChatResponse)
async def cold_start(request: ColdStartRequest):
    """冷启动 - 生成破冰消息"""
    try:
        config = _resolve_runtime_config(request.api_key, request.model)
        controller = _get_controller(config)
        controller.reset()
        result = await controller.start_cold_start()
        return ChatResponse(
            reply=result["reply"],
            suggestions=result["suggestions"],
            current_mode=controller.get_current_mode(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/reply", response_model=ChatResponse)
async def reply(request: ReplyRequest):
    """处理用户回复（建议卡点击或手动输入）"""
    try:
        config = _resolve_runtime_config(request.api_key, request.model)
        controller = _get_controller(config)
        
        if request.choice:
            result = await controller.handle_suggestion_click(request.choice, request.text)
        else:
            result = await controller.handle_manual_input(request.text)
        
        return ChatResponse(
            reply=result["reply"],
            suggestions=result["suggestions"],
            current_mode=controller.get_current_mode(),
            mode_changed=result.get("mode_changed"),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/mode-toggle", response_model=ModeToggleResponse)
async def mode_toggle(request: ModeToggleRequest):
    """模式切换请求"""
    global _controller
    
    if _controller is None:
        raise HTTPException(status_code=400, detail="请先调用 cold-start 初始化会话")
    
    result = _controller.state.request_mode_change(request.target_mode)
    return ModeToggleResponse(
        accepted=result.accepted,
        current_mode=_controller.get_current_mode(),
        reason=result.reason,
    )


@router.post("/reset")
async def reset_session():
    """重置会话"""
    global _controller
    if _controller:
        _controller.reset()
    return {"status": "ok"}


@router.get("/state")
async def get_state():
    """获取当前状态（调试用）"""
    global _controller
    if _controller is None:
        return {"initialized": False}
    return {
        "initialized": True,
        **_controller.get_state(),
    }

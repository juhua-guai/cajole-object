# -*- coding: utf-8 -*-
"""FastAPI 应用入口"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from src.api.routes.chat import router as chat_router

PROJECT_ROOT = Path(__file__).parent.parent.parent

app = FastAPI(
    title="布布的嘴替日常 - Web API",
    description="沉浸式恋爱互动 Web 版后端",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=PROJECT_ROOT / "static"), name="static")

app.include_router(chat_router, prefix="/api/chat", tags=["chat"])


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

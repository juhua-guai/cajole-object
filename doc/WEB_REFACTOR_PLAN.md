# Web 版重构开发计划

## 现有项目分析

| 项目 | 说明 |
|------|------|
| 当前技术栈 | PyQt6 桌面应用 + LangChain + OpenAI |
| 可复用模块 | `StateManager`、`LLMService`、`EmotionAnalyzer`、`ChatController`（已具备异步支持） |
| 目标技术栈 | React/Next.js 前端 + Python FastAPI 后端 |

---

## 里程碑 M1: 前端骨架 + 设置弹层 + 冷启动 + 建议卡点击

| 序号 | 任务 | 说明 |
|------|------|------|
| 1.1 | 创建 FastAPI 后端入口 | 新建 `src/api/main.py`，配置 CORS、静态文件服务 |
| 1.2 | 实现 `/api/chat/cold-start` 接口 | 接收配置参数，调用 `ChatController.start_cold_start()` |
| 1.3 | 实现 `/api/chat/reply` 接口 | 处理建议卡点击和手动输入，返回 reply + suggestions + mode |
| 1.4 | 初始化 Next.js 前端项目 | 在项目根目录创建 `web/` 文件夹，使用 `create-next-app` |
| 1.5 | 实现配置管理模块 | LocalStorage 读写 `bubu-config`（apiKey/model） |
| 1.6 | 创建设置弹层组件 | 表单编辑配置、保存/重置按钮、安全提示 |
| 1.7 | 创建 Header 组件 | 模式指示器、设置入口按钮 |
| 1.8 | 创建 ChatArea 组件 | 消息气泡流（布布左侧、一二右侧）、头像圆形裁剪 |
| 1.9 | 创建 SuggestionBar 组件 | A/B/C 三张卡片、情绪图标、点击态和 loading 态 |
| 1.10 | 实现冷启动流程 | 页面加载时调用接口，展示布布回复 + 建议卡 |
| 1.11 | 实现建议卡点击流程 | 点击后调用 `/api/chat/reply`，更新对话和建议卡 |

---

## 里程碑 M2: 完整模式逻辑 + 情绪识别 + LLM 接入

| 序号 | 任务 | 说明 |
|------|------|------|
| 2.1 | 实现 `/api/chat/mode-toggle` 接口 | 处理模式切换请求，返回 accepted/reason |
| 2.2 | 重构后端配置传递 | 从请求头/body 读取前端配置，动态创建 LLMService |
| 2.3 | 创建 InputBar 组件 | 折叠/展开文本输入框、发送按钮 |
| 2.4 | 实现手动输入流程 | 发送文本 → 后端情绪识别 → 返回回复 |
| 2.5 | 前端模式状态管理 | Context 管理 mode/desiredMode/happyCount/angryCount |
| 2.6 | 实现模式切换UI | Header 模式开关按钮、切换动画、pending 提示 |
| 2.7 | 实现自动模式切换提示 | 模式变化时 Toast 提醒用户 |
| 2.8 | 对话历史管理 | 前端维护 history 数组（最近10轮）、"清空会话"按钮 |

---

## 里程碑 M3: 异常兜底 + 资源占位 + 移动端适配

| 序号 | 任务 | 说明 |
|------|------|------|
| 3.1 | 后端异常处理完善 | 捕获 LLM 429/余额不足，返回友好错误信息 |
| 3.2 | 前端错误提示组件 | Toast/Modal 展示 API 错误 |
| 3.3 | 情绪识别失败兜底 | 后端异常时回退情绪 B |
| 3.4 | 输入乱码兜底 | 返回预设熊言熊语吐槽文案 |
| 3.5 | 头像资源优化 | 复用 `static/avatars/`，实现 fallback 占位图 |
| 3.6 | 情绪图标集成 | 建议卡显示对应情绪图标 |
| 3.7 | 响应式布局 | 移动端适配，气泡宽度、输入框调整 |
| 3.8 | 基础样式优化 | 统一配色、字体、动画过渡 |
| 3.9 | 集成测试 | 端到端流程验证 |

---

## 技术要点

### 后端 (Python FastAPI)

- FastAPI + 现有 `ChatController`（已支持异步）
- 单用户内存会话，无需数据库
- 配置通过请求动态传递，支持即时生效
- 静态文件服务：复用 `static/` 目录

### 前端 (Next.js)

- Next.js 14 + React 18
- 状态管理: React Context
- 样式: Tailwind CSS
- API 调用: fetch

### 资源复用

| 模块 | 路径 | 说明 |
|------|------|------|
| StateManager | `src/state_manager.py` | 模式/计数状态管理，完整复用 |
| LLMService | `src/llm_service.py` | LLM 调用与响应解析，完整复用 |
| EmotionAnalyzer | `src/emotion_analyzer.py` | 情绪识别，完整复用 |
| ChatController | `src/chat_controller.py` | 聊天控制器，已支持异步，完整复用 |
| 静态资源 | `static/` | 头像、图标等资源 |

---

## 目录结构预览

```
cajole-object/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI 入口
│   │   └── routes/
│   │       └── chat.py          # 聊天相关接口
│   ├── chat_controller.py       # 复用
│   ├── state_manager.py         # 复用
│   ├── llm_service.py           # 复用
│   ├── emotion_analyzer.py      # 复用
│   └── ...
├── web/                         # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx         # 主页面
│   │   │   └── layout.tsx
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── ChatArea.tsx
│   │   │   ├── SuggestionBar.tsx
│   │   │   ├── InputBar.tsx
│   │   │   └── SettingsModal.tsx
│   │   ├── contexts/
│   │   │   └── ChatContext.tsx
│   │   └── lib/
│   │       ├── api.ts           # API 调用封装
│   │       └── config.ts        # LocalStorage 配置管理
│   └── ...
├── static/                      # 静态资源（复用）
│   ├── avatars/
│   ├── icons/
│   └── placeholder/
└── ...
```

---

## 接口定义

### POST /api/chat/cold-start

**请求体:**
```json
{
  "api_key": "string",
  "model": "string"
}
```

**响应:**
```json
{
  "reply": "string",
  "suggestions": [
    { "label": "A", "text": "string" },
    { "label": "B", "text": "string" },
    { "label": "C", "text": "string" }
  ],
  "current_mode": "roast" | "survival"
}
```

### POST /api/chat/reply

**请求体:**
```json
{
  "text": "string",
  "choice": "A" | "B" | "C" | null,
  "api_key": "string",
  "model": "string"
}
```

**响应:**
```json
{
  "reply": "string",
  "suggestions": [...],
  "current_mode": "roast" | "survival",
  "mode_changed": "to_survival" | "to_roast" | null
}
```

### POST /api/chat/mode-toggle

**请求体:**
```json
{
  "target_mode": "roast" | "survival"
}
```

**响应:**
```json
{
  "accepted": true | false,
  "current_mode": "roast" | "survival",
  "reason": "already_in_mode" | "pending_emotion_confirm" | "emotion_supported"
}
```

---

## 启动命令

### 后端
```bash
# 安装依赖
uv add fastapi uvicorn

# 启动
uvicorn src.api.main:app --reload --port 8000
```

### 前端
```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 同时启动
```bash
# 可使用 concurrently 或分别在两个终端启动
```

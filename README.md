# cajole-object

布布的嘴替日常，包含 FastAPI 后端与 Next.js 前端。

## 安全配置

推荐优先使用后端服务端配置，不要把真实密钥提交进仓库。

可用环境变量：

- `CAJOLE_API_KEY`
- `CAJOLE_MODEL_NAME`
- `CAJOLE_MAX_HISTORY_ROUNDS`

也可以复制 `config.example.toml` 为 `config.toml` 本地使用。`config.toml` 已被 `.gitignore` 忽略，不应提交真实凭据。

## 本地运行

后端：

```bash
export CAJOLE_API_KEY="your_api_key"
uv run uvicorn src.api.main:app --reload
```

前端：

```bash
cd web
npm run dev
```

## 前端密钥策略

前端默认优先使用后端服务端配置。

如果你在设置里临时输入 API Key：

- 只保存在当前浏览器标签页会话中
- 刷新或关闭标签页后需要重新输入
- 不会写入仓库文件

## 开源前检查

```bash
git status --ignored
```

确认以下内容处于 ignored 状态：

- `config.toml`
- `.env*`
- `.venv/`
- `.idea/`

# SEO Agent — 启动指南

> 一个自用的 SEO 自动化工具，灵感来自 Nicholas Dulait 的 ChatSEO 26 步法 + 50 Agent 体系。
> 通过 MCP 协议把 Google Search Console 数据暴露给 Claude Desktop / Cursor / ChatGPT。

## 1. 一次性安装

### 1.1 准备 Python 环境

本项目用 hermes 自带的 venv（已经装好 `mcp` 和 `requests`）：

```bash
PYTHON=/home/ubuntu/.hermes/hermes-agent/venv/bin/python
$PYTHON --version
```

如果想用独立 venv：

```bash
python3 -m venv ~/venvs/seo-agent
source ~/venvs/seo-agent/bin/activate
pip install mcp requests
```

### 1.2 准备 GSC 凭证

参照本会话上文用户在 Google Cloud Console 建的 OAuth 2.0 Client（Desktop 类型）。
把 `client_id` 和 `client_secret` 写到 `~/.hermes/.env`（**不要**写到项目目录、笔记目录、聊天里）：

```bash
mkdir -p ~/.hermes
cat > ~/.hermes/.env <<'EOF'
GSC_CLIENT_ID=xxxxx.apps.googleusercontent.com
GSC_CLIENT_SECRET=GOCSPX-xxx
GSC_REDIRECT_URI=http://localhost:8765
EOF
chmod 600 ~/.hermes/.env
```

> ⚠️ **不要把 .env 提交到 git、不要写到 /home/ubuntu/notes/（会被坚果云同步）**

### 1.3 跑 OAuth 授权

```bash
cd /home/ubuntu/notes/projects/seo-agent
$PYTHON -m mcp_server.auth.gsc_oauth
```

会自动：
1. 打开浏览器跳到 Google 登录
2. 你点「允许」
3. 回调到 `http://localhost:8765`
4. 换 token 存到 `~/.hermes/gsc_token.json`（600 权限）

**如果之前已经授权过同一个 app**：Google 不会给新的 refresh_token。
先到 https://myaccount.google.com/permissions 撤销本 app，再重跑。

### 1.4 验证 token 拿得到 sites

```bash
$PYTHON -m mcp_server.gsc_client
```

应该输出你 GSC 已验证的网站列表。

---

## 2. 接进 Claude Desktop

编辑 Claude Desktop 配置文件：

- macOS：`~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows：`%APPDATA%\Claude\claude_desktop_config.json`
- Linux：`~/.config/Claude/claude_desktop_config.json`

把 `docs/claude_desktop_config.json` 内容合并进去（已经有 `mcpServers` 字段就追加）：

```json
{
  "mcpServers": {
    "seo": {
      "command": "/home/ubuntu/.hermes/hermes-agent/venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/home/ubuntu/notes/projects/seo-agent"
    }
  }
}
```

重启 Claude Desktop。在新对话里应该能看到 4 个新工具：
- `list_my_sites`
- `gsc_top_queries_tool`
- `gsc_top_pages_tool`
- `gsc_opportunities_tool`

试试：

> "列出我 GSC 已授权的 site"

> "用 `gsc_top_queries_tool` 查 https://example.com/ 过去 28 天高展示词"

> "用 `gsc_opportunities_tool` 找流量机会"

---

## 3. 接进 Cursor

类似，编辑 `~/.cursor/mcp.json`（或 Cursor Settings → MCP）。

---

## 4. 测试某个工具

不接 MCP host 也能直接调：

```bash
$PYTHON -m mcp_server.tools.gsc_top_pages
```

会打印过去 28 天 top 20 页面 + 「差一点上首页」的机会。

---

## 5. 故障排查

### `CookieLoadError: failed to load cookies` / `RefreshError: invalid_grant`
- `gsc_token.json` 损坏或 refresh_token 失效
- 去 https://myaccount.google.com/permissions 撤销 → 重跑 OAuth 脚本

### `403 Access denied`
- 你 GSC 里没验证这个 site
- 在 GSC 添加 site 然后重跑

### `Access blocked: This app's request is invalid`
- OAuth client 的 redirect URI 没配 `http://localhost:8765`
- 回 Google Cloud Console → Credentials → 你的 OAuth client → Authorized redirect URIs → 加上

### `python3 -m mcp_server.server` 启动后没反应
- 这是正常的（stdin/stdout 协议在等 MCP host）
- 必须在 MCP host 里调

---

## 6. 重要：把 secrets 放在对的地方

| 文件 | 放哪 | 权限 |
|---|---|---|
| `GSC_CLIENT_ID` / `SECRET` | `~/.hermes/.env` | `600` |
| `gsc_token.json`（refresh_token） | `~/.hermes/gsc_token.json` | `600` |
| 项目代码 | `/home/ubuntu/notes/projects/seo-agent/` | 普通 |
| prompt 库 / skill 文档 | 项目目录 | 普通（**别**含 secret） |

**绝对不要**：
- ❌ 把 secret 写到 `/home/ubuntu/notes/`（会被坚果云同步到手机/电脑）
- ❌ 把 secret 写进任何 .md 笔记
- ❌ 把 secret 贴到聊天截图（OCR 抓得到）
- ❌ 把 secret commit 到 git

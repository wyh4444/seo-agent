---
name: seo-agent
description: "SEO 自动化工具包——通过 MCP 协议把 Google Search Console 实时数据暴露给 LLM agent。基于 Nicholas Dulait 的 ChatSEO 26 步法 + 50 Agent 体系。"
version: 0.1.0
---

# SEO Agent (Self-hosted)

A self-hosted SEO automation toolkit that exposes Google Search Console data to any LLM agent via the Model Context Protocol (MCP).

Inspired by [ChatSEO](https://chatseo.app/) and the work of [Nicholas Dulait](https://x.com/nicholasdulait) — particularly his 26-step Claude SEO playbook and 50 Agent / 50 Skill architecture.

## What's included

- **MCP server** exposing 4 GSC tools: `list_my_sites`, `gsc_top_queries`, `gsc_top_pages`, `gsc_opportunities`
- **One-time OAuth flow** with PKCE (no service account needed)
- **Auto token refresh** (refresh_token silently swaps access_token each call)
- **Reusable prompt library** (the 26-step playbook, ready to copy-paste)
- **50 Agent / 50 Skill template structure** (you fill in your own prompts)

## Quick start

```bash
# 1. Install
git clone https://github.com/YOUR_ORG/seo-agent.git ~/projects/seo-agent
cd ~/projects/seo-agent
python3 -m venv .venv
source .venv/bin/activate
pip install mcp requests

# 2. Set GSC credentials (NEVER commit these)
mkdir -p ~/.hermes
cat > ~/.hermes/.env <<EOF
GSC_CLIENT_ID=xxxxx.apps.googleusercontent.com
GSC_CLIENT_SECRET=GOCSPX-xxxxx
GSC_REDIRECT_URI=http://localhost:8765
EOF
chmod 600 ~/.hermes/.env

# 3. One-time OAuth flow
python -m mcp_server.auth.gsc_oauth
# → opens browser, you click "Allow", token saved to ~/.hermes/gsc_token.json

# 4. Verify
python -m mcp_server.gsc_client
# → lists your GSC sites

# 5. Connect to Claude Desktop / Cursor / Hermes
# See docs/STARTUP.md
```

## Use in any MCP host

### Claude Desktop

Edit `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "seo": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["-m", "mcp_server.server"],
      "cwd": "/absolute/path/to/seo-agent"
    }
  }
}
```

### Hermes

Edit `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  - name: seo
    command: /absolute/path/to/.venv/bin/python
    args: ["-m", "mcp_server.server"]
    cwd: /absolute/path/to/seo-agent
```

### Cursor

Edit `~/.cursor/mcp.json` with the same shape.

## The 4 GSC tools

### `list_my_sites`
Returns the GSC sites you have access to (with permission level).

### `gsc_top_queries`
Top queries by impressions / clicks / position over the last N days.

### `gsc_top_pages`
Top pages by impressions — pair with `gsc_top_queries` to see what each page ranks for.

### `gsc_opportunities` ⭐
**The money tool.** Returns queries where you rank 8-15 with high impressions and low CTR — the "almost on page 1" sweet spot. Title/meta fixes here have the best ROI.

## Roadmap

- [ ] DataForSEO integration (keyword research + on-page audit + rank tracking)
- [ ] Chief of SEO Agent (4 jobs: diagnosis / opportunity / click capture / experiments)
- [ ] 50 Agent / 50 Skill prompt library
- [ ] Cron-driven weekly audit reports

## Security

- `~/.hermes/.env` contains OAuth client secret — never commit, never sync
- `~/.hermes/gsc_token.json` contains refresh_token — never commit, never sync
- See `docs/STARTUP.md` for troubleshooting

## License

Apache 2.0

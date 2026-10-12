# seo-agent

A self-hosted SEO automation toolkit that exposes Google Search Console data to any LLM agent via the Model Context Protocol (MCP).

Inspired by [ChatSEO](https://chatseo.app/) and Nicholas Dulait's 26-step Claude SEO playbook + 50 Agent / 50 Skill architecture.

**4 GSC tools in one MCP server:**
- `list_my_sites` — your authorized GSC sites
- `gsc_top_queries` — top queries over a time window
- `gsc_top_pages` — top pages over a time window
- `gsc_opportunities` ⭐ — queries ranking 8-15 with high impressions & low CTR (best title/meta fix ROI)

Works with Claude Desktop, Cursor, and Hermes — anywhere that speaks MCP.

## Quick start

```bash
git clone https://github.com/YOUR_ORG/seo-agent.git
cd seo-agent
python3 -m venv .venv && source .venv/bin/activate
pip install mcp requests
```

Then follow [`docs/STARTUP.md`](docs/STARTUP.md) for the OAuth setup + MCP host connection.

## Why

Most AI SEO advice is generic because the model has never seen your site. The fix: let the model query your real Search Console data. This server is the minimal viable version of that — 4 tools, no UI, no subscription, runs locally.

## Roadmap

- [x] GSC OAuth with PKCE + auto refresh
- [x] 4 GSC tools exposed via MCP
- [ ] DataForSEO integration (keyword research + on-page audit + rank tracking)
- [ ] Chief of SEO Agent (4 jobs)
- [ ] 50 Agent / 50 Skill prompt library
- [ ] Scheduled weekly audits

## License

Apache 2.0

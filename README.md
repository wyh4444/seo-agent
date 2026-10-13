# seo-agent

Self-hosted SEO automation toolkit that exposes Google Search Console + DataForSEO data to any LLM agent via MCP.

Inspired by [ChatSEO](https://chatseo.app/) and Nicholas Dulait's 26-step Claude SEO playbook + 14-skill architecture (1 Chief + 4 departments: research / optimize / grow / measure).

## What's inside

### MCP server (8 tools)
- **GSC (4)**: `list_my_sites`, `gsc_top_queries_tool`, `gsc_top_pages_tool`, `gsc_opportunities_tool`
- **DataForSEO (3 + 1 status)**: `keyword_research_tool`, `audit_page_tool`, `rank_check_tool`, `is_mock_mode_tool`

### 14 Skills
- **Chief** ([`chief_of_seo/AGENT.md`](chief_of_seo/AGENT.md)) — 4 件事: 诊断 / 机会 / 点击 / 实验
- **Research (4)**: [`skills/research/`](skills/research/) — keyword-research, search-intent-analysis, competitor-gap-analysis, topical-map-builder
- **Optimize (4)**: [`skills/optimize/`](skills/optimize/) — title-meta-rewriter, on-page-audit-fix, content-brief-generator, internal-link-architect
- **Grow (3)**: [`skills/grow/`](skills/grow/) — backlink-opportunity-finder, brand-mention-tracker, pr-pitch-generator
- **Measure (3)**: [`skills/measure/`](skills/measure/) — weekly-audit-report, ab-experiment-designer, ranking-decline-investigator

Index: [`skills/INDEX.md`](skills/INDEX.md)

### 26-Step Playbook
- [`prompts/01_install/`](prompts/01_install/) — Setup (steps 1-4)
- [`prompts/02_keywords/`](prompts/02_keywords/) — Keyword research (steps 5-7)
- [`prompts/03_template/`](prompts/03_template/) — Page templates (steps 8-15)
- [`prompts/04_per_page/`](prompts/04_per_page/) — Per-page production (steps 16-19)
- [`prompts/05_pacing/`](prompts/05_pacing/) — Pacing & scaling (steps 20-26)

## Quick start

```bash
git clone https://github.com/YOUR_ORG/seo-agent.git
cd seo-agent
python3 -m venv .venv && source .venv/bin/activate
pip install mcp requests
```

Then follow [`docs/STARTUP.md`](docs/STARTUP.md) for the OAuth setup + MCP host connection.

## Status

| Week | Scope | Status |
|---|---|---|
| W1 | GSC OAuth + 4 GSC tools | ✅ shipped |
| W2 | DataForSEO skeleton (mock) + Research 4 skills + Playbook stages 1-2 | ✅ shipped |
| W3 | Chief of SEO + Optimize 4 + Grow 3 + Measure 3 + Playbook stages 3-5 | ✅ shipped |
| W4 (planned) | DataForSEO real API + GEO/AI search visibility (xAI) | ⏳ next |

## License

Apache 2.0

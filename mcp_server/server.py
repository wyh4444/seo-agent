"""SEO Agent MCP Server —— 入口

把 GSC + DataForSEO 工具暴露给 Claude Desktop / Cursor / ChatGPT 任何 MCP host。

启动方式（手动）：
    cd /home/ubuntu/notes/projects/seo-agent
    /home/ubuntu/.hermes/hermes-agent/venv/bin/python -m mcp_server.server

Claude Desktop 接入：在 claude_desktop_config.json 加：
    {
      "mcpServers": {
        "seo": {
          "command": "/home/ubuntu/.hermes/hermes-agent/venv/bin/python",
          "args": ["-m", "mcp_server.server"],
          "cwd": "/home/ubuntu/notes/projects/seo-agent"
        }
      }
    }
"""
from mcp.server.fastmcp import FastMCP
from .tools.gsc_top_queries import gsc_top_queries
from .tools.gsc_top_pages import gsc_top_pages, gsc_opportunities
from .gsc_client import list_sites
from .dataforseo_client import keyword_research, keyword_ideas, audit_page, rank_check, is_mock_mode
from .xai_client import ask_about_brand, geo_audit, generate_brand_questions, is_xai_mock

mcp = FastMCP("seo-agent")


@mcp.tool()
def list_my_sites() -> list[dict]:
    """列出 GSC 已授权的所有 site（含 permission level）。
    第一步工具：不知道 site URL 时先用这个查。
    """
    return list_sites()


@mcp.tool()
def gsc_top_queries_tool(
    site_url: str,
    days: int = 28,
    min_impressions: int = 100,
    limit: int = 50,
    sort_by: str = "impressions",
) -> list[dict]:
    """从 Google Search Console 拉过去 N 天高展示量关键词。

    Args:
        site_url: GSC 里的 site URL（用 list_my_sites 查）
        days: 回看天数（默认 28，最大 16 个月）
        min_impressions: 过滤掉低于 N impressions 的长尾词
        limit: 最多返回条数
        sort_by: impressions / clicks / position

    Returns:
        [{"query", "clicks", "impressions", "ctr", "position"}]
    """
    return gsc_top_queries(site_url, days, min_impressions, limit, sort_by)


@mcp.tool()
def gsc_top_pages_tool(
    site_url: str,
    days: int = 28,
    min_impressions: int = 100,
    limit: int = 50,
) -> list[dict]:
    """从 GSC 拉过去 N 天高展示量页面。

    Returns:
        [{"page", "clicks", "impressions", "ctr", "position"}]
    """
    return gsc_top_pages(site_url, days, min_impressions, limit)


@mcp.tool()
def gsc_opportunities_tool(
    site_url: str,
    days: int = 28,
    min_impressions: int = 500,
    max_position: float = 15.0,
    min_ctr: float = 0.01,
    limit: int = 30,
) -> list[dict]:
    """【核心】找出「排名 8-15 + 高展示 + 低 CTR」的关键词 = 典型流量机会。

    选这个甜蜜区的原因：
        - 排名 8-15 的页面已经在第 2 页或首页底部，**差一点上首页**
        - 高 impressions 意味着 Google 觉得这个 query 相关
        - 低 CTR 意味着 title/meta 写得不够吸引人

    修 title/meta 性价比最高的场景。

    Returns:
        [{"query", "page", "clicks", "impressions", "ctr", "position", "potential_clicks"}]
    """
    return gsc_opportunities(site_url, days, min_impressions, max_position, min_ctr, limit)


# ---- DataForSEO 工具（mock 驱动，未接真实 API） ----

@mcp.tool()
def keyword_research_tool(
    query: str,
    country: str = "US",
) -> dict:
    """关键词研究：volume / CPC / difficulty / intent。

    ⚠️ 当前为 mock 模式（DataForSEO 凭证未配）。结果含 `_source: "mock"`，**不要当真**。
    接入真实 API：把 DataForSEO login/password 写到 ~/.hermes/.env 的 DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD。

    Args:
        query: 要研究的关键词
        country: ISO 国家代码（US / CN / GB 等），默认 US

    Returns:
        {"keyword", "volume", "cpc_usd", "difficulty_0_100", "intent", "competition_level", "_source"}
    """
    return keyword_research(query, country)


@mcp.tool()
def keyword_ideas_tool(
    seed: str,
    country: str = "US",
    limit: int = 20,
) -> list[dict]:
    """关键词扩展：基于 seed 找 N 个相关长尾词。

    ⚠️ 当前为 mock 模式。
    Args:
        seed: 种子关键词
        country: ISO 国家代码，默认 US
        limit: 最多返回条数
    Returns:
        [{"keyword", "volume", "cpc_usd", "difficulty_0_100", "_source"}]
    """
    return keyword_ideas(seed, country, limit)


@mcp.tool()
def audit_page_tool(url: str) -> dict:
    """站内 on-page 审计：title / meta / headings / links / speed。

    ⚠️ 当前为 mock 模式。
    Args:
        url: 要审计的完整 URL
    Returns:
        {"url", "seo_score", "title", "title_length", "meta_description",
         "h1_count", "word_count", "internal_links", "external_links",
         "images_missing_alt", "page_speed_estimate", "issues", "_source"}
    """
    return audit_page(url)


@mcp.tool()
def rank_check_tool(
    keyword: str,
    country: str = "US",
) -> dict:
    """查某关键词当前排名（实时 SERP 第一个有机结果）。

    ⚠️ 当前为 mock 模式。
    Args:
        keyword: 要查的关键词
        country: ISO 国家代码，默认 US
    Returns:
        {"keyword", "country", "rank", "url", "title", "search_volume", "_source"}
    """
    return rank_check(keyword, country)


@mcp.tool()
def is_mock_mode_tool() -> dict:
    """检查 DataForSEO 是否在 mock 模式。"""
    return {"dataforseo_mock": is_mock_mode(),
            "xai_mock": is_xai_mock(),
            "reason_dataforseo": "DATAFORSEO_LOGIN / DATAFORSEO_PASSWORD 未在 ~/.hermes/.env 配置"
                       if is_mock_mode() else "credentials found",
            "reason_xai": "XAI_API_KEY 未在 ~/.hermes/.env 配置" if is_xai_mock() else "credentials found"}


# ---- xAI / GEO 工具（GEO 监测：AI 答案里你的品牌出现频率） ----

@mcp.tool()
def ask_about_brand_tool(brand: str, question: str) -> dict:
    """【GEO 监测】问 Grok 一个关于品牌/产品的问题，看 AI 答案里你品牌被提了几次。

    ⚠️ 当前为 mock 模式（XAI_API_KEY 未配）。结果含 `_source: "mock"`，**不要当真**。
    接入真实 API：把 xAI API key 写到 ~/.hermes/.env 的 XAI_API_KEY。

    Args:
        brand: 监测的品牌/产品/网站名
        question: 问 AI 的问题（**不要含 brand**，让 AI 自然提）

    Returns:
        {"question", "brand", "mentioned" (bool), "mention_count", "cited_sources", "raw_answer", "_source"}
    """
    return ask_about_brand(brand, question)


@mcp.tool()
def geo_audit_tool(brand: str, count: int = 10) -> dict:
    """【GEO 审计】批量问 Grok N 个关于品牌的问题，统计提及率。

    适合每月做一次：你的品牌在 AI 答案里"出现率"是多少？

    ⚠️ 当前为 mock 模式。
    Args:
        brand: 监测的品牌
        count: 问 N 个问题（默认 10），自动从模板生成

    Returns:
        {"brand", "questions_asked", "mention_count", "mention_rate", "details", "_source"}
    """
    questions = generate_brand_questions(brand, count=count)
    return geo_audit(brand, questions)


if __name__ == "__main__":
    mcp.run()

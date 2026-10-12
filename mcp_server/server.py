"""SEO Agent MCP Server —— 入口

把 GSC 工具暴露给 Claude Desktop / Cursor / ChatGPT 任何 MCP host。

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


if __name__ == "__main__":
    mcp.run()

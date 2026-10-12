"""GSC 工具 1：top_queries

用法（从 Python 直接调）：
    from mcp_server.tools import gsc_top_queries
    gsc_top_queries("https://example.com/", days=28, min_impressions=200, limit=50)

返回：
    [
      {"query": "best crm for small business", "clicks": 23, "impressions": 1800, "ctr": 0.0128, "position": 11.4},
      ...
    ]
"""
from datetime import datetime, timedelta
from typing import Literal
from ..gsc_client import call


def _default_dates(days: int) -> tuple[str, str]:
    end = datetime.utcnow() - timedelta(days=3)  # GSC 有 2-3 天延迟
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def gsc_top_queries(
    site_url: str,
    days: int = 28,
    min_impressions: int = 100,
    limit: int = 100,
    sort_by: Literal["impressions", "clicks", "position"] = "impressions",
) -> list[dict]:
    """从 GSC 拉过去 N 天高展示量关键词（按 impressions 降序）。

    site_url: GSC 里的 site URL（必须是你授权时包含的 site）
              例：'https://example.com/' 或 'sc-domain:example.com'
    days: 回看天数（默认 28 天）
    min_impressions: 过滤掉 impressions < N 的长尾词（避免返回几千条噪声）
    limit: 最多返回几条
    sort_by: impressions / clicks / position
    """
    start_date, end_date = _default_dates(days)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query"],
        "rowLimit": min(limit * 3, 25000),  # 多拉一些，后面客户端再过滤
    }
    # sort_by 在 GSC API 里用 searchType + 自定义排序不能直接做，先拉后处理
    data = call("POST", f"/sites/{site_url}/searchAnalytics/query", body=body)

    rows = data.get("rows", [])
    out = []
    for r in rows:
        out.append({
            "query": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"], 4),
            "position": round(r["position"], 1),
        })

    # 客户端过滤 + 排序
    out = [q for q in out if q["impressions"] >= min_impressions]
    if sort_by == "impressions":
        out.sort(key=lambda x: -x["impressions"])
    elif sort_by == "clicks":
        out.sort(key=lambda x: -x["clicks"])
    elif sort_by == "position":
        out.sort(key=lambda x: x["position"])  # 升序
    return out[:limit]


if __name__ == "__main__":
    # 快速自检
    from ..gsc_client import list_sites
    sites = list_sites()
    if not sites:
        print("⚠️  没有已授权的 site。先在 GSC 验证网站并重跑 OAuth。")
    else:
        site = sites[0]["siteUrl"]
        print(f"\n== {site} top 20 queries (过去 28 天, min 50 impressions) ==\n")
        for q in gsc_top_queries(site, days=28, min_impressions=50, limit=20):
            print(f"  {q['position']:5.1f}  {q['ctr']:6.2%}  "
                  f"imp={q['impressions']:5d}  clk={q['clicks']:4d}  "
                  f"{q['query']}")

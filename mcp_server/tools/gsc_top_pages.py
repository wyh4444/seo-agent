"""GSC 工具 2：top_pages

按 page 维度拉数据，找出最有潜力优化的页面。
配合 top_queries 一起用：先看 page 的整体表现，再看这个 page 吃下了哪些 query。
"""
from datetime import datetime, timedelta
from ..gsc_client import call


def _default_dates(days: int) -> tuple[str, str]:
    end = datetime.utcnow() - timedelta(days=3)
    start = end - timedelta(days=days)
    return start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d")


def gsc_top_pages(
    site_url: str,
    days: int = 28,
    min_impressions: int = 100,
    limit: int = 50,
) -> list[dict]:
    """拉过去 N 天高展示量页面。

    返回字段：
        page, clicks, impressions, ctr, position
    """
    start_date, end_date = _default_dates(days)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["page"],
        "rowLimit": min(limit * 3, 25000),
    }
    data = call("POST", f"/sites/{site_url}/searchAnalytics/query", body=body)
    rows = data.get("rows", [])
    out = []
    for r in rows:
        out.append({
            "page": r["keys"][0],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": round(r["ctr"], 4),
            "position": round(r["position"], 1),
        })
    out = [p for p in out if p["impressions"] >= min_impressions]
    out.sort(key=lambda x: -x["impressions"])
    return out[:limit]


def gsc_opportunities(
    site_url: str,
    days: int = 28,
    min_impressions: int = 500,
    max_position: float = 15.0,
    min_ctr: float = 0.01,
    limit: int = 50,
) -> list[dict]:
    """Chief of SEO 第 2 件事的核心数据：
    找出「排名 8-15 + 高展示 + 低 CTR」的 query——典型「差一点上首页」的机会。

    默认参数：
        排名 8-15：处于"差一点上首页"的甜蜜区
        impressions >= 500：流量潜力够大
        CTR < 1%：title/meta 大概率没吸引力
    """
    start_date, end_date = _default_dates(days)
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "dimensions": ["query", "page"],
        "rowLimit": min(limit * 5, 25000),
    }
    data = call("POST", f"/sites/{site_url}/searchAnalytics/query", body=body)
    rows = data.get("rows", [])

    out = []
    for r in rows:
        query, page = r["keys"]
        pos = r["position"]
        ctr = r["ctr"]
        imp = r["impressions"]
        if 8.0 <= pos <= max_position and imp >= min_impressions and ctr < min_ctr:
            out.append({
                "query": query,
                "page": page,
                "clicks": r["clicks"],
                "impressions": imp,
                "ctr": round(ctr, 4),
                "position": round(pos, 1),
                # 估算如果 CTR 提到首页均值的潜在点击增量
                "potential_clicks": round(imp * 0.08, 0),  # 首页均值粗估 8%
            })
    # 按潜在点击增量降序
    out.sort(key=lambda x: -x["potential_clicks"])
    return out[:limit]


def _opportunities_from_rows(
    rows: list[dict],
    min_impressions: int = 500,
    max_position: float = 15.0,
    min_ctr: float = 0.01,
    limit: int = 50,
) -> list[dict]:
    """纯函数版: 从 GSC raw rows 算 opportunities。便于测试。

    输入 rows 格式: [{query, page, clicks, impressions, ctr, position}, ...]
    """
    out = []
    for r in rows:
        if not (8.0 <= r["position"] <= max_position):
            continue
        if r["impressions"] < min_impressions:
            continue
        if r["ctr"] >= min_ctr:
            continue
        out.append({
            "query": r["query"],
            "page": r["page"],
            "clicks": r["clicks"],
            "impressions": r["impressions"],
            "ctr": r["ctr"],
            "position": r["position"],
            "potential_clicks": round(r["impressions"] * 0.08, 0),
        })
    out.sort(key=lambda x: -x["potential_clicks"])
    return out[:limit]


if __name__ == "__main__":
    from ..gsc_client import list_sites
    sites = list_sites()
    if not sites:
        print("⚠️  没有已授权的 site。")
    else:
        site = sites[0]["siteUrl"]
        print(f"\n== {site} 流量机会（排名 8-15 + 高展示 + 低 CTR）==\n")
        opps = gsc_opportunities(site, days=28, min_impressions=500, limit=20)
        if not opps:
            print("  没有匹配的机会（试试调低 min_impressions 或调宽 position 范围）")
        for o in opps:
            print(f"  pos={o['position']:5.1f}  ctr={o['ctr']:6.2%}  "
                  f"imp={o['impressions']:5d}  +pot={o['potential_clicks']:5.0f}/月  "
                  f"{o['query'][:50]}")
            print(f"    → {o['page'][:80]}")

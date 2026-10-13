#!/usr/bin/env python3
"""自动 SEO 周报脚本。

用法:
    python scripts/weekly_report.py --site "https://example.com/"
    python scripts/weekly_report.py --site "https://example.com/" --geo-brand "MyBrand"

输出:
    1. stdout: markdown 报告
    2. 文件: ./weekly_report_YYYYMMDD.md
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 让脚本能 import mcp_server（不依赖 mcp 库）
sys.path.insert(0, str(Path(__file__).parent.parent))


def _safe_call(fn, *args, **kwargs):
    """调一个函数，失败时返回空 + 错误标记，不让脚本崩。"""
    try:
        return {"ok": True, "data": fn(*args, **kwargs)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def build_report(site_url: str, geo_brand: str = None) -> str:
    """生成 markdown 周报。"""
    from mcp_server.tools.gsc_top_queries import gsc_top_queries
    from mcp_server.tools.gsc_top_pages import gsc_top_pages, gsc_opportunities
    from mcp_server.gsc_client import list_sites

    today = datetime.now()
    week_start = today - timedelta(days=7)

    lines = []
    lines.append(f"# SEO 周报: {site_url}")
    lines.append(f"")
    lines.append(f"**周期**: {week_start.strftime('%Y-%m-%d')} - {today.strftime('%Y-%m-%d')}")
    lines.append(f"**生成时间**: {today.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # ---- 1. 整体数据 ----
    lines.append("## 1. 整体数据")
    lines.append("")
    queries_7d = _safe_call(gsc_top_queries, site_url, days=7, min_impressions=0, limit=10000, sort_by="clicks")
    if not queries_7d["ok"]:
        lines.append(f"❌ GSC 数据拉取失败: {queries_7d['error']}")
        lines.append("")
        return "\n".join(lines)

    rows = queries_7d["data"]
    total_clicks = sum(r["clicks"] for r in rows)
    total_impressions = sum(r["impressions"] for r in rows)
    avg_position = (
        sum(r["position"] * r["impressions"] for r in rows) / total_impressions
        if total_impressions else 0
    )

    lines.append(f"- **总 clicks**: {total_clicks:,}")
    lines.append(f"- **总 impressions**: {total_impressions:,}")
    lines.append(f"- **加权平均 position**: {avg_position:.1f}")
    lines.append(f"- **活跃 query 数**: {len(rows):,}")
    lines.append("")

    # ---- 2. Top 5 queries (by clicks) ----
    lines.append("## 2. Top 5 queries (按 clicks)")
    lines.append("")
    lines.append("| Query | Clicks | Impressions | Position | CTR |")
    lines.append("|---|---:|---:|---:|---:|")
    for r in rows[:5]:
        lines.append(f"| {r['query']} | {r['clicks']} | {r['impressions']} | {r['position']:.1f} | {r['ctr']:.2%} |")
    lines.append("")

    # ---- 3. 流量机会 ----
    lines.append("## 3. 流量机会 (排名 8-15, 高展示, 低 CTR)")
    lines.append("")
    opps = _safe_call(gsc_opportunities, site_url, days=28, min_impressions=500, limit=10)
    if opps["ok"] and opps["data"]:
        lines.append("| Query | Position | Impressions | CTR | Potential | Page |")
        lines.append("|---|---:|---:|---:|---:|---|")
        for o in opps["data"][:10]:
            lines.append(
                f"| {o['query']} | {o['position']:.1f} | {o['impressions']:,} | "
                f"{o['ctr']:.2%} | +{o['potential_clicks']:.0f} | {o['page'][:50]} |"
            )
    else:
        lines.append("（无）")
    lines.append("")

    # ---- 4. GEO 监测 (可选) ----
    if geo_brand:
        from mcp_server.xai_client import geo_audit, generate_brand_questions, is_xai_mock
        lines.append(f"## 4. GEO 监测: {geo_brand}")
        lines.append("")
        if is_xai_mock():
            lines.append("⚠️ xAI mock 模式 — 数据是 fake")
        questions = generate_brand_questions(geo_brand, count=10)
        audit = _safe_call(geo_audit, geo_brand, questions)
        if audit["ok"]:
            a = audit["data"]
            lines.append(f"- **AI 答案中提及率**: {a['mention_rate']:.0%} ({a['mention_count']}/{a['questions_asked']})")
        else:
            lines.append(f"❌ GEO 失败: {audit['error']}")
        lines.append("")

    # ---- 5. 模式状态 ----
    lines.append("## 5. 模式状态")
    from mcp_server.dataforseo_client import is_mock_mode
    from mcp_server.xai_client import is_xai_mock
    lines.append("")
    lines.append(f"- DataForSEO: {'mock' if is_mock_mode() else 'real'}")
    lines.append(f"- xAI: {'mock' if is_xai_mock() else 'real'}")
    lines.append("")

    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(description="SEO 周报生成器")
    p.add_argument("--site", required=True, help="GSC site URL, 例如 https://example.com/")
    p.add_argument("--geo-brand", help="要监测 GEO 提及率的品牌名")
    p.add_argument("--out", help="输出文件路径 (默认 ./weekly_report_YYYYMMDD.md)")
    args = p.parse_args()

    report = build_report(args.site, args.geo_brand)
    print(report)

    if args.out:
        out_path = args.out
    else:
        today = datetime.now().strftime("%Y%m%d")
        out_path = f"weekly_report_{today}.md"
    Path(out_path).write_text(report)
    print(f"\n📄 报告已保存到: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()

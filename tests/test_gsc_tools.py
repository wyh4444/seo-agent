"""GSC 工具测试 — gsc_top_queries / gsc_top_pages / gsc_opportunities。

不连真实 API（需要 GSC OAuth），只测：
- 工具函数的形状
- 参数校验 / 默认值
- opportunities 排名范围过滤
"""
import pytest


def test_top_queries_signature():
    from mcp_server.tools.gsc_top_queries import gsc_top_queries
    import inspect
    sig = inspect.signature(gsc_top_queries)
    params = sig.parameters
    assert "site_url" in params
    assert "days" in params
    assert "min_impressions" in params
    assert "limit" in params
    assert "sort_by" in params
    # sort_by default = "impressions"
    assert params["sort_by"].default == "impressions"
    # days default = 28
    assert params["days"].default == 28


def test_top_pages_signature():
    from mcp_server.tools.gsc_top_pages import gsc_top_pages
    import inspect
    sig = inspect.signature(gsc_top_pages)
    params = sig.parameters
    assert "site_url" in params
    assert "days" in params
    assert params["days"].default == 28


def test_opportunities_filters_by_position():
    """opportunities 工具应过滤 position 8-15 范围。"""
    from mcp_server.tools.gsc_top_pages import _opportunities_from_rows
    rows = [
        {"query": "too_high", "page": "/p1", "clicks": 10, "impressions": 5000, "ctr": 0.002, "position": 5.0},
        {"query": "sweet", "page": "/p2", "clicks": 20, "impressions": 3000, "ctr": 0.006, "position": 12.0},
        {"query": "too_low", "page": "/p3", "clicks": 30, "impressions": 4000, "ctr": 0.007, "position": 18.0},
    ]
    # 默认 max_position=15, min_position=8 → sweet 在, too_high / too_low 都被滤
    out = _opportunities_from_rows(
        rows, min_impressions=500, max_position=15.0, min_ctr=0.01, limit=30
    )
    queries = [x["query"] for x in out]
    assert "too_high" not in queries  # position 5 < 8 下限
    assert "too_low" not in queries   # position 18 > 15 上限
    assert "sweet" in queries          # position 12 ∈ [8, 15]


def test_opportunities_filters_by_impressions():
    from mcp_server.tools.gsc_top_pages import _opportunities_from_rows
    rows = [
        {"query": "high", "page": "/p1", "clicks": 10, "impressions": 5000, "ctr": 0.002, "position": 10.0},
        {"query": "low", "page": "/p2", "clicks": 5, "impressions": 100, "ctr": 0.05, "position": 9.0},
    ]
    out = _opportunities_from_rows(
        rows, min_impressions=500, max_position=15.0, min_ctr=0.5, limit=30
    )
    # high: ctr=0.002 < 0.5 → pass
    # low: impressions 100 < 500 → fail
    queries = [x["query"] for x in out]
    assert "high" in queries
    assert "low" not in queries


def test_opportunities_potential_clicks_calc():
    """potential_clicks 应基于 impressions × 假设的 page-1 CTR 算。"""
    from mcp_server.tools.gsc_top_pages import _opportunities_from_rows
    rows = [
        {"query": "q", "page": "/p", "clicks": 10, "impressions": 1000, "ctr": 0.005, "position": 10.0},
    ]
    out = _opportunities_from_rows(
        rows, min_impressions=500, max_position=15.0, min_ctr=0.01, limit=30
    )
    assert len(out) == 1
    assert "potential_clicks" in out[0]
    # 1000 imp × 8% = 80 potential_clicks
    assert out[0]["potential_clicks"] == 80
    assert out[0]["potential_clicks"] > out[0]["clicks"]

"""DataForSEO client 测试 — 覆盖 mock 路径 + 解析函数。

不连真实 API（凭据未配），只测：
- mock 数据形状正确
- 解析函数（_parse_*）边界条件
- 错误处理
"""
import os
import sys
from pathlib import Path

import pytest

# 跑测试前确认在 mock mode
assert os.environ.get("DATAFORSEO_LOGIN") is None, "测试应只在 mock mode 跑"


def test_is_mock_mode():
    from mcp_server.dataforseo_client import is_mock_mode
    assert is_mock_mode() is True


def test_keyword_research_mock():
    from mcp_server.dataforseo_client import keyword_research
    r = keyword_research("test query")
    assert r["_source"] == "mock"
    assert "volume" in r
    assert r["volume"] > 0
    assert r["intent"] in ("transactional", "commercial", "informational", "navigational")
    assert 0 <= r["difficulty_0_100"] <= 100


def test_keyword_research_deterministic():
    """同 query 永远返回同结果（mock 用 hash）。"""
    from mcp_server.dataforseo_client import keyword_research
    a = keyword_research("deterministic test")
    b = keyword_research("deterministic test")
    assert a == b


def test_keyword_ideas_mock():
    from mcp_server.dataforseo_client import keyword_ideas
    ideas = keyword_ideas("best crm", limit=5)
    assert len(ideas) == 5
    assert all("_source" in x for x in ideas)
    assert all("keyword" in x for x in ideas)


def test_audit_page_mock():
    from mcp_server.dataforseo_client import audit_page
    r = audit_page("https://example.com/")
    assert r["_source"] == "mock"
    assert "seo_score" in r
    assert 0 <= r["seo_score"] <= 100
    assert "issues" in r
    assert isinstance(r["issues"], list)


def test_rank_check_mock():
    from mcp_server.dataforseo_client import rank_check
    r = rank_check("seo tools")
    assert r["_source"] == "mock"
    assert "rank" in r
    assert r["rank"] is not None


# ---- 解析函数测试 ----

def test_infer_intent_transactional():
    from mcp_server.dataforseo_client import _infer_intent
    assert _infer_intent("buy crm software") == "transactional"
    assert _infer_intent("crm pricing") == "transactional"


def test_infer_intent_commercial():
    from mcp_server.dataforseo_client import _infer_intent
    assert _infer_intent("best crm 2026") == "commercial"
    assert _infer_intent("crm vs hubspot") == "commercial"


def test_infer_intent_navigational():
    from mcp_server.dataforseo_client import _infer_intent
    assert _infer_intent("hubspot login") == "navigational"
    assert _infer_intent("crm official website") == "navigational"


def test_infer_intent_informational_default():
    from mcp_server.dataforseo_client import _infer_intent
    assert _infer_intent("how to use crm") == "informational"
    assert _infer_intent("what is crm") == "informational"


def test_parse_keyword_volume_empty():
    from mcp_server.dataforseo_client import _parse_keyword_volume
    r = _parse_keyword_volume({"result": [{}]})
    assert r["keyword"] is None
    assert r["volume"] == 0
    assert r["cpc_usd"] == 0.0
    assert r["_source"] == "dataforseo"


def test_parse_keyword_volume_full():
    from mcp_server.dataforseo_client import _parse_keyword_volume
    task = {"result": [{
        "keyword": "best crm",
        "search_volume": 12000,
        "cpc": 4.5,
        "competition": 0.65,
        "competition_level": "HIGH",
    }]}
    r = _parse_keyword_volume(task)
    assert r["keyword"] == "best crm"
    assert r["volume"] == 12000
    assert r["cpc_usd"] == 4.5
    assert r["difficulty_0_100"] == 65
    assert r["competition_level"] == "high"


def test_parse_serp_skips_paid():
    """SERP 解析必须跳过 paid 结果。"""
    from mcp_server.dataforseo_client import _parse_serp
    task = {"result": [{
        "keyword": "best crm",
        "location_name": "United States",
        "search_volume": 12500,
        "items": [
            {"type": "paid", "url": "https://ads.com", "title": "Ads", "rank_absolute": 1},
            {"type": "organic", "rank_absolute": 1, "url": "https://hubspot.com", "title": "HubSpot"},
        ]
    }]}
    r = _parse_serp(task)
    assert r["rank"] == 1
    assert r["url"] == "https://hubspot.com"
    assert r["title"] == "HubSpot"


def test_parse_serp_no_organic():
    from mcp_server.dataforseo_client import _parse_serp
    task = {"result": [{
        "keyword": "test",
        "location_name": "US",
        "search_volume": 0,
        "items": [{"type": "paid"}]
    }]}
    r = _parse_serp(task)
    assert r["rank"] is None
    assert r["url"] is None


def test_parse_serp_empty():
    from mcp_server.dataforseo_client import _parse_serp
    r = _parse_serp({"result": [{}]})
    assert r["rank"] is None
    assert r["_source"] == "dataforseo"


def test_dataforseo_post_no_credentials():
    """无凭证时 _dataforseo_post 应该 raise。"""
    from mcp_server.dataforseo_client import _dataforseo_post
    with pytest.raises(RuntimeError, match="凭证未配置"):
        _dataforseo_post("test/endpoint", [])

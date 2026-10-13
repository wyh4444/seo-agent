"""xAI client 测试 — 覆盖 mock 路径。

不连真实 API（XAI_API_KEY 未配），只测：
- mock 数据形状
- brand 提及判定
- 默认问题模板
"""
import os
import pytest

assert os.environ.get("XAI_API_KEY") is None, "测试应只在 mock mode 跑"


def test_is_xai_mock():
    from mcp_server.xai_client import is_xai_mock
    assert is_xai_mock() is True


def test_ask_about_brand_mentioned():
    from mcp_server.xai_client import ask_about_brand
    r = ask_about_brand("Notion", "What's Notion and is it any good?")
    assert r["mentioned"] is True
    assert r["mention_count"] >= 1
    assert r["_source"] == "mock"


def test_ask_about_brand_not_mentioned():
    from mcp_server.xai_client import ask_about_brand
    r = ask_about_brand("Notion", "Best project management tools")
    assert r["mentioned"] is False
    assert r["mention_count"] == 0


def test_generate_brand_questions():
    from mcp_server.xai_client import generate_brand_questions, DEFAULT_BRAND_QUESTIONS
    qs = generate_brand_questions("Notion", count=5)
    assert len(qs) == 5
    assert all("Notion" in q for q in qs)
    # count 超过模板数 → 截断到模板数
    qs_all = generate_brand_questions("Notion", count=100)
    assert len(qs_all) == len(DEFAULT_BRAND_QUESTIONS)
    # count=0 不应 crash
    assert generate_brand_questions("Notion", count=0) == []


def test_geo_audit_mention_rate():
    from mcp_server.xai_client import geo_audit
    # 5 个问题里 2 个含 brand
    qs = [
        "What is Notion?",
        "Best project tools",
        "Notion vs Trello",
        "How to write notes",
        "Notion pricing review",
    ]
    audit = geo_audit("Notion", qs)
    assert audit["questions_asked"] == 5
    assert audit["mention_count"] == 3
    assert audit["mention_rate"] == 0.6
    assert len(audit["details"]) == 5
    assert audit["_source"] == "mock"


def test_geo_audit_empty():
    from mcp_server.xai_client import geo_audit
    audit = geo_audit("Notion", [])
    assert audit["questions_asked"] == 0
    assert audit["mention_rate"] == 0

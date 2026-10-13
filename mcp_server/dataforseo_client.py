"""DataForSEO 客户端骨架（mock 驱动）。

设计原则：
- **mock 优先**：没有真实 API key 时，return hardcoded 但合理的 mock 数据
- **接口预留**：DataForSEO 的接口签名在 docstring 里写清楚，接真实 API 时只改这部分
- **配置入口统一**：所有密钥从 ~/.hermes/.env 读

真实接入步骤（等用户准备好 DataForSEO 账号时改这里）：
1. 用户充值并拿到 login + password
2. 写到 ~/.hermes/.env：DATAFORSEO_LOGIN=xxx，DATAFORSEO_PASSWORD=***
3. 把 use_mock() 函数逻辑改成"有 key 就调真 API，没有就 mock"
4. 调 DataForSEO 的 endpoint（POST + Basic Auth + JSON body）
"""
import os
import json
import hashlib
from pathlib import Path
from typing import Any


def _get_credentials() -> tuple[str | None, str | None]:
    env_path = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_path):
        return None, None
    env = {}
    for line in Path(env_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env.get("DATAFORSEO_LOGIN"), env.get("DATAFORSEO_PASSWORD")


def is_mock_mode() -> bool:
    """是否走 mock 路径（没有 DataForSEO 凭证）"""
    login, password = _get_credentials()
    return not (login and password)


# ---- Keyword research mock ----
# 用 query 字符串 hash 出确定性的 mock 数据（同一 query 永远返回相同数据，便于测试）
def _mock_keyword_data(query: str) -> dict:
    h = int(hashlib.md5(query.encode()).hexdigest()[:8], 16)
    volume = 100 + (h % 50000)
    cpc = round(0.1 + (h % 100) / 10, 2)
    difficulty = (h % 100)
    # 搜索意图基于 query 关键词猜
    q = query.lower()
    if any(w in q for w in ["buy", "price", "best", "review", "vs", "alternative", "cheap"]):
        intent = "transactional"
    elif any(w in q for w in ["how", "what", "why", "guide", "tutorial", "learn"]):
        intent = "informational"
    elif any(w in q for w in ["login", "download", "official", "website"]):
        intent = "navigational"
    else:
        intent = "commercial"
    return {
        "keyword": query,
        "volume": volume,
        "cpc_usd": cpc,
        "difficulty_0_100": difficulty,
        "intent": intent,
        "competition_level": "high" if difficulty > 70 else "medium" if difficulty > 30 else "low",
        "_source": "mock",
    }


# ---- Audit mock ----
def _mock_audit(url: str) -> dict:
    h = int(hashlib.md5(url.encode()).hexdigest()[:8], 16)
    score = 50 + (h % 50)
    return {
        "url": url,
        "seo_score": score,
        "title": "Page Title (audit by mock)",
        "title_length": 30 + (h % 30),
        "meta_description": f"Meta description for {url[:50]}...",
        "h1_count": 1 if h % 3 == 0 else 2,
        "word_count": 500 + (h % 2000),
        "internal_links": 5 + (h % 20),
        "external_links": 1 + (h % 5),
        "images_missing_alt": h % 4,
        "page_speed_estimate": "fast" if h % 3 != 0 else "slow",
        "issues": [
            {"severity": "warning", "msg": "Title tag length sub-optimal"},
            {"severity": "info", "msg": "Add more internal links"},
        ] if score < 70 else [],
        "_source": "mock",
    }


# ---- Rank tracker mock ----
def _mock_rank(keyword: str, country: str = "US") -> dict:
    h = int(hashlib.md5((keyword + country).encode()).hexdigest()[:8], 16)
    return {
        "keyword": keyword,
        "country": country,
        "rank": 1 + (h % 100),
        "url": f"https://example.com/page-{h % 50}",
        "title": f"Mock result for {keyword}",
        "search_volume": 100 + (h % 5000),
        "_source": "mock",
    }


# ---- 真实 API 调用骨架 ----
# 详细 endpoint：
# - keywords_data/google_ads/search_volume/live   ($0.05/1k)
# - dataforseo_labs/google/bulk_keyword_difficulty/live   ($0.05/1k)
# - dataforseo_labs/google/keyword_ideas/live   ($0.10/1k)
# - dataforseo_labs/google/keyword_overview/live   ($0.10/1k)
# - on_page/instant_pages   ($0.30/page)
# - serp/google/organic/live/advanced   ($0.50/1k SERP, 100 results each)


def _dataforseo_post(endpoint: str, body: list) -> list[dict]:
    """调真实 DataForSEO API（等用户接入凭证后启用）。

    DataForSEO API 模式：
    - URL: https://api.dataforseo.com/v3/{endpoint}
    - Method: POST
    - Auth: Basic base64(login:password)
    - Body: list of tasks（不是单个 object）
    - 返回: {tasks: [{status_code, result: [...]}]}

    详细 endpoint：
    - keywords_data/google_ads/search_volume/live
    - dataforseo_labs/google/keyword_ideas/live
    - on_page/instant_pages
    - serp/google/organic/live/advanced

    Task status_code 参考：20000 = success; 40400/40401 = task not found; 40000-40999 = client error
    """
    import base64
    import requests

    login, password = _get_credentials()
    if not (login and password):
        raise RuntimeError("DataForSEO 凭证未配置")

    creds = base64.b64encode(f"{login}:{password}".encode()).decode()
    resp = requests.post(
        f"https://api.dataforseo.com/v3/{endpoint}",
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )
    resp.raise_for_status()  # 4xx/5xx 立刻抛，避免 silent fail
    data = resp.json()
    tasks = data.get("tasks", [])
    # DataForSEO 200 状态但 task.status_code 可能非 0（业务错误）
    if tasks and tasks[0].get("status_code", 0) != 20000:
        raise RuntimeError(f"DataForSEO task error: {tasks[0].get('status_message')}")
    return tasks


# ---- 真实 API 响应解析 ----

def _parse_keyword_volume(task: dict) -> dict:
    """从 keywords_data/google_ads/search_volume/live 的 task 解析。

    DataForSEO 返回结构（task.result[0]）:
        keyword: str
        search_volume: int | None
        cpc: float | None
        competition: float | None  (0-1)
        competition_level: "LOW" | "MEDIUM" | "HIGH" | None
        monthly_searches: [{year, month, search_volume}]
    """
    item = (task.get("result") or [{}])[0]
    competition = item.get("competition")
    return {
        "keyword": item.get("keyword"),
        "volume": item.get("search_volume") or 0,
        "cpc_usd": round(item.get("cpc") or 0.0, 2),
        "difficulty_0_100": int((competition or 0) * 100),
        "intent": _infer_intent(item.get("keyword", "")),
        "competition_level": (item.get("competition_level") or "UNKNOWN").lower(),
        "monthly_trend": item.get("monthly_searches", [])[-12:],  # 最近 12 月
        "_source": "dataforseo",
    }


def _parse_keyword_ideas(task: dict) -> list[dict]:
    """从 dataforseo_labs/google/keyword_ideas/live 解析。

    task.result[0].items: [{keyword, search_volume, cpc, competition, ...}]
    """
    items = (task.get("result") or [{}])[0].get("items") or []
    return [
        {
            "keyword": x.get("keyword"),
            "volume": x.get("search_volume") or 0,
            "cpc_usd": round(x.get("cpc") or 0.0, 2),
            "difficulty_0_100": int((x.get("competition") or 0) * 100),
            "_source": "dataforseo",
        }
        for x in items
    ]


def _parse_onpage(task: dict) -> dict:
    """从 on_page/instant_pages 解析。

    task.result[0] 包含: items[0] (主结果), crawled_pages, redirects, broken_links, etc.
    """
    result = task.get("result") or [{}]
    items = result[0].get("items") or [{}]
    page = items[0]
    checks = page.get("checks") or {}
    issues = []
    for sev, k in (("error", "is_broken"), ("warning", "is_redirect"), ("info", "no_title")):
        if checks.get(k):
            issues.append({"severity": sev, "msg": k})
    title = page.get("meta", {}).get("title", "")
    return {
        "url": page.get("url"),
        "seo_score": _onpage_score(page),
        "title": title,
        "title_length": len(title),
        "meta_description": page.get("meta", {}).get("description", ""),
        "h1_count": len(page.get("meta", {}).get("h1", []) or []),
        "word_count": page.get("content", {}).get("plain_text_word_count", 0) or page.get("content", {}).get("total_word_count", 0),
        "internal_links": page.get("links_internal_count", 0),
        "external_links": page.get("links_external_count", 0),
        "images_missing_alt": page.get("content", {}).get("images_count_without_alt", 0),
        "page_speed_estimate": "fast" if checks.get("high_loading_time") is False else "slow",
        "issues": issues,
        "_source": "dataforseo",
    }


def _onpage_score(page: dict) -> int:
    """简单 0-100 评分（On-Page API 没现成 score，自己算）。"""
    score = 100
    if page.get("meta", {}).get("title") in (None, ""): score -= 30
    elif not (30 <= len(page.get("meta", {}).get("title", "")) <= 65): score -= 10
    if page.get("meta", {}).get("description") in (None, ""): score -= 15
    if page.get("checks", {}).get("no_title"): score -= 10
    if page.get("checks", {}).get("is_broken"): score -= 50
    if page.get("content", {}).get("images_count_without_alt", 0) > 0: score -= 5
    if (page.get("links_internal_count") or 0) < 3: score -= 10
    return max(0, score)


def _parse_serp(task: dict) -> dict:
    """从 serp/google/organic/live/advanced 解析第一个有机结果。

    task.result[0].items[0] = 第一个 organic item，包含 rank_absolute, url, title
    """
    items = (task.get("result") or [{}])[0].get("items") or []
    organic = [x for x in items if x.get("type") == "organic"]
    if not organic:
        return {
            "keyword": (task.get("result") or [{}])[0].get("keyword"),
            "country": (task.get("result") or [{}])[0].get("location_name"),
            "rank": None,
            "url": None,
            "title": None,
            "search_volume": (task.get("result") or [{}])[0].get("search_volume"),
            "_source": "dataforseo",
        }
    first = organic[0]
    result = (task.get("result") or [{}])[0]
    return {
        "keyword": result.get("keyword"),
        "country": result.get("location_name"),
        "rank": first.get("rank_absolute"),
        "url": first.get("url"),
        "title": first.get("title"),
        "search_volume": result.get("search_volume"),
        "_source": "dataforseo",
    }


def _infer_intent(keyword: str) -> str:
    """从关键词推搜索意图（DataForSEO 不直接给，用启发式）。"""
    k = keyword.lower()
    if any(w in k for w in ["buy", "price", "pricing", "discount", "coupon", "deal", "order", "shop", "cheap"]):
        return "transactional"
    if any(w in k for w in ["best", "review", "vs", "alternative", "comparison", "top", "compare"]):
        return "commercial"
    if any(w in k for w in ["login", "official", "download", "website"]):
        return "navigational"
    return "informational"


# ---- 公开 API（mock / 真实两套共用入口） ----


def keyword_research(query: str, country: str = "US") -> dict:
    """关键词研究：volume / CPC / difficulty / intent。

    真实 API: keywords_data/google_ads/search_volume/live
    """
    if is_mock_mode():
        return _mock_keyword_data(query)
    tasks = _dataforseo_post(
        "keywords_data/google_ads/search_volume/live",
        [{"keywords": [query], "location_name": _country_to_location(country)}],
    )
    return _parse_keyword_volume(tasks[0])


def keyword_ideas(seed: str, country: str = "US", limit: int = 20) -> list[dict]:
    """关键词扩展：基于 seed 找相关长尾词。"""
    if is_mock_mode():
        # mock：用 mock_keyword_data 派生一些变体
        import random
        suffixes = ["for small business", "for solopreneur", "vs hubspot", "review",
                    "alternative", "free", "cheap", "2026", "comparison", "best"]
        out = []
        for s in suffixes[:limit]:
            out.append(_mock_keyword_data(f"{seed} {s}"))
        return out
    tasks = _dataforseo_post(
        "dataforseo_labs/google/keyword_ideas/live",
        [{
            "keywords": [seed],
            "location_name": _country_to_location(country),
            "limit": limit,
        }],
    )
    return _parse_keyword_ideas(tasks[0])


def audit_page(url: str) -> dict:
    """站内 on-page 审计：title / meta / headings / links / speed。

    真实 API: on_page/instant_pages ($0.30/page)
    """
    if is_mock_mode():
        return _mock_audit(url)
    tasks = _dataforseo_post("on_page/instant_pages", [{"url": url}])
    return _parse_onpage(tasks[0])


def rank_check(keyword: str, country: str = "US") -> dict:
    """查某关键词当前排名第一的有机结果。"""
    if is_mock_mode():
        return _mock_rank(keyword, country)
    tasks = _dataforseo_post(
        "serp/google/organic/live/advanced",
        [{
            "keyword": keyword,
            "location_name": _country_to_location(country),
            "depth": 10,  # 只看前 10，省钱
        }],
    )
    return _parse_serp(tasks[0])


# ---- 工具函数 ----
def _country_to_location(country_code: str) -> str:
    """DataForSEO 用 location_name 而不是 country code。"""
    mapping = {"US": "United States", "CN": "China", "GB": "United Kingdom"}
    return mapping.get(country_code, country_code)


if __name__ == "__main__":
    print(f"Mock mode: {is_mock_mode()}")
    print()
    print("== keyword_research('best crm for small business') ==")
    print(json.dumps(keyword_research("best crm for small business"), indent=2, ensure_ascii=False))
    print()
    print("== audit_page('https://example.com/') ==")
    print(json.dumps(audit_page("https://example.com/"), indent=2, ensure_ascii=False))
    print()
    print("== rank_check('seo tools 2026') ==")
    print(json.dumps(rank_check("seo tools 2026"), indent=2, ensure_ascii=False))

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


# ---- 真实 API 调用骨架（未启用） ----
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
    resp.raise_for_status()
    return resp.json().get("tasks", [])


# ---- 公开 API（mock / 真实两套共用入口） ----
def keyword_research(query: str, country: str = "US") -> dict:
    """关键词研究：volume / CPC / difficulty / intent。

    真实 API 切换：把下面 if is_mock_mode() 改成 if False 即可调真 API。
    """
    if is_mock_mode():
        return _mock_keyword_data(query)
    # TODO: 真实 DataForSEO 调用
    # tasks = _dataforseo_post(
    #     "keywords_data/google_ads/search_volume/live",
    #     [{"keywords": [query], "location_name": _country_to_location(country)}],
    # )
    # return _parse_keyword_volume(tasks[0])
    return _mock_keyword_data(query)  # fallback


def audit_page(url: str) -> dict:
    """站内 on-page 审计：title/meta/headings/links/speed 等。"""
    if is_mock_mode():
        return _mock_audit(url)
    # TODO: 真实 DataForSEO On-Page API
    # tasks = _dataforseo_post("on_page/instant_pages", [{"url": url}])
    # return _parse_onpage_result(tasks[0])
    return _mock_audit(url)


def rank_check(keyword: str, country: str = "US") -> dict:
    """查某关键词当前排名（实时 SERP）。"""
    if is_mock_mode():
        return _mock_rank(keyword, country)
    # TODO: 真实 DataForSEO SERP API
    # tasks = _dataforseo_post(
    #     "serp/google/organic/live/advanced",
    #     [{"keyword": keyword, "location_name": _country_to_location(country), "depth": 100}],
    # )
    # return _parse_serp_first(tasks[0])
    return _mock_rank(keyword, country)


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

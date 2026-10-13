"""xAI (Grok) Live Search 客户端。

作用: GEO (Generative Engine Optimization) 监测。
- 问 Grok 你的品牌 / 产品 / 网站 → 看他怎么答
- 多久提一次？提的时候用没用 source?
- 跟竞品对比: 谁被 AI 提得更多

API: https://api.x.ai/v1/chat/completions (model: grok-4-fast-reasoning 或 grok-4-1-fast-reasoning)
参数: search_parameters.mode = "on" (开启 X / web 搜索)
"""
import os
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any


def _get_api_key() -> str | None:
    env_path = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_path):
        return None
    for line in Path(env_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k.strip() == "XAI_API_KEY":
            return v.strip()
    return None


def is_xai_mock() -> bool:
    """是否走 mock 路径（无 XAI_API_KEY）"""
    return not _get_api_key()


# ---- mock 模式 ----
def _mock_brand_query(brand: str, question: str) -> dict:
    """Mock 回答：基于 brand 是否在 question 中决定提及率。"""
    mentioned = brand.lower() in question.lower()
    return {
        "question": question,
        "brand": brand,
        "mentioned": mentioned,
        "mention_count": 1 if mentioned else 0,
        "cited_sources": [],
        "raw_answer": f"[mock] Grok 回答: 这是关于 '{question}' 的模拟回答{(', 包含 ' + brand) if mentioned else ''}.",
        "_source": "mock",
    }


def _mock_geo_audit(brand: str, questions: list[str]) -> dict:
    return {
        "brand": brand,
        "audit_window": "mock",
        "questions_asked": len(questions),
        "mention_count": sum(1 for q in questions if brand.lower() in q.lower()),
        "mention_rate": sum(1 for q in questions if brand.lower() in q.lower()) / max(1, len(questions)),
        "details": [_mock_brand_query(brand, q) for q in questions],
        "_source": "mock",
    }


# ---- 真实 API ----
def _xai_chat(messages: list[dict], model: str = "grok-4-fast-reasoning",
               enable_search: bool = True) -> dict:
    """调 xAI /v1/chat/completions, 用 urllib (避免 requests 依赖)."""
    api_key = _get_api_key()
    if not api_key:
        raise RuntimeError("XAI_API_KEY 未配置")

    body = {
        "model": model,
        "messages": messages,
    }
    if enable_search:
        # Live Search 开启
        body["search_parameters"] = {
            "mode": "on",
            # "sources": [{"type": "news"}, {"type": "x"}, {"type": "web"}],
        }

    req = urllib.request.Request(
        "https://api.x.ai/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())


# ---- 公开 API ----
def ask_about_brand(brand: str, question: str,
                    model: str = "grok-4-fast-reasoning") -> dict:
    """问 Grok 关于某品牌/产品/网站的问题，看他怎么答。

    Args:
        brand: 你想监测的品牌/产品/网站名
        question: 给 Grok 的问题（不要含 brand，让它自然提）

    Returns:
        {
            "question", "brand", "mentioned" (bool),
            "mention_count", "cited_sources", "raw_answer", "_source"
        }
    """
    if is_xai_mock():
        return _mock_brand_query(brand, question)

    try:
        data = _xai_chat(
            messages=[{"role": "user", "content": question}],
            model=model,
            enable_search=True,
        )
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        raise RuntimeError(f"xAI API 调用失败: {e}")

    # 解析
    choice = (data.get("choices") or [{}])[0]
    msg = choice.get("message") or {}
    answer = msg.get("content", "")

    # 提取 cited sources（从 message 里; xAI 用 citations 字段）
    cited = msg.get("citations") or []

    # 简单判定 mentioned
    mentioned = brand.lower() in answer.lower()
    mention_count = answer.lower().count(brand.lower())

    return {
        "question": question,
        "brand": brand,
        "mentioned": mentioned,
        "mention_count": mention_count,
        "cited_sources": cited,
        "raw_answer": answer,
        "model": model,
        "_source": "xai",
    }


def geo_audit(brand: str, questions: list[str],
              model: str = "grok-4-fast-reasoning") -> dict:
    """批量问 Grok N 个问题，统计品牌提及率。

    Args:
        brand: 品牌名
        questions: 候选问题列表（10-30 条）
        model: 用的 xAI 模型

    Returns:
        {
            "brand", "questions_asked", "mention_count",
            "mention_rate" (0-1), "details" (list), "_source"
        }
    """
    if is_xai_mock():
        return _mock_geo_audit(brand, questions)

    details = []
    for q in questions:
        try:
            details.append(ask_about_brand(brand, q, model=model))
        except Exception as e:
            details.append({
                "question": q, "brand": brand, "mentioned": False,
                "mention_count": 0, "cited_sources": [],
                "raw_answer": f"[error: {e}]", "_source": "xai",
            })

    mention_count = sum(1 for d in details if d.get("mentioned"))
    return {
        "brand": brand,
        "questions_asked": len(questions),
        "mention_count": mention_count,
        "mention_rate": mention_count / max(1, len(questions)),
        "details": details,
        "model": model,
        "_source": "xai",
    }


# ---- 工具函数 ----
DEFAULT_BRAND_QUESTIONS = [
    "What's the best {brand} for small business?",
    "Recommend a {brand} alternative",
    "How does {brand} compare to competitors?",
    "Is {brand} worth it in 2026?",
    "Top 5 tools like {brand}",
    "{brand} vs HubSpot",
    "{brand} pricing review",
    "Best {brand} for startups",
    "Pros and cons of {brand}",
    "What do users think about {brand}?",
]


def generate_brand_questions(brand: str, count: int = 10) -> list[str]:
    """生成 N 个会问 AI 的候选问题（基于 brand）。"""
    templates = DEFAULT_BRAND_QUESTIONS[:count]
    return [t.format(brand=brand) for t in templates]


if __name__ == "__main__":
    print(f"xAI mock mode: {is_xai_mock()}")
    print()
    brand = "Notion"
    questions = generate_brand_questions(brand, count=5)
    print(f"Generated {len(questions)} questions for brand '{brand}'")
    audit = geo_audit(brand, questions)
    print()
    print(f"Mention rate: {audit['mention_rate']:.0%} ({audit['mention_count']}/{audit['questions_asked']})")

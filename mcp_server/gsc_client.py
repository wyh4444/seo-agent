"""GSC API 客户端封装：自动用 refresh_token 静默换 access_token。

所有 mcp_server/tools 下的脚本都从这里调，不要直接调 Google API。
"""
import json
import os
import time
import requests
from pathlib import Path
from typing import Any

TOKEN_FILE = "/home/ubuntu/.hermes/gsc_token.json"
ENV_FILE = os.path.expanduser("~/.hermes/.env")
API_BASE = "https://www.googleapis.com/webmasters/v3"


def _load_env() -> dict:
    """从 ~/.hermes/.env 读 GSC_CLIENT_ID / GSC_CLIENT_SECRET。

    一次 fallback 也不留 — 死代码和误用风险 > 兼容性价值。
    旧位置 /home/ubuntu/notes/_work/.env 已废弃。
    """
    env_path = os.path.expanduser("~/.hermes/.env")
    if not os.path.exists(env_path):
        raise FileNotFoundError(
            f"找不到 {env_path}。请先创建并写入 GSC_CLIENT_ID / GSC_CLIENT_SECRET / GSC_REDIRECT_URI"
        )
    env = {}
    for line in Path(env_path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    required = {"GSC_CLIENT_ID", "GSC_CLIENT_SECRET"}
    missing = required - set(env.keys())
    if missing:
        raise ValueError(f"~/.hermes/.env 缺少字段: {missing}")
    return env


def _load_token() -> dict:
    if not os.path.exists(TOKEN_FILE):
        raise FileNotFoundError(
            f"找不到 {TOKEN_FILE}。先跑 python mcp_server/auth/gsc_oauth.py"
        )
    return json.loads(Path(TOKEN_FILE).read_text())


def _save_token(tok: dict) -> None:
    Path(TOKEN_FILE).write_text(json.dumps(tok, indent=2, ensure_ascii=False))
    os.chmod(TOKEN_FILE, 0o600)


def _refresh_if_needed() -> dict:
    tok = _load_token()
    # 我们没存 expires_at 时间戳，每次调用都主动 verify 一下
    # 简单做法：直接拿现有 access_token 试，失败再 refresh
    return tok


def _get_access_token() -> str:
    tok = _refresh_if_needed()
    return tok["access_token"]


def _ensure_valid_token() -> str:
    """调一次轻量 API，失败就 refresh，重试一次。"""
    tok = _load_token()
    headers = {"Authorization": f"Bearer {tok['access_token']}"}
    # 拿 sites 列表做 health check
    r = requests.get(f"{API_BASE}/sites", headers=headers, timeout=15)
    if r.status_code == 401:
        # refresh
        env = _load_env()
        resp = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": env["GSC_CLIENT_ID"],
                "client_secret": env["GSC_CLIENT_SECRET"],
                "refresh_token": tok["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=15,
        )
        resp.raise_for_status()
        new_tok = resp.json()
        tok.update(new_tok)
        _save_token(tok)
        return tok["access_token"]
    if not r.ok:
        raise RuntimeError(f"GSC API error {r.status_code}: {r.text}")
    return tok["access_token"]


def call(method: str, path: str, **params) -> Any:
    """统一 GSC API 调用入口。

    用法：
        call("GET", "/sites")
        call("POST", "/sites/{siteUrl}/searchAnalytics/query", body=..., dimensions=...)
    """
    token = _ensure_valid_token()
    url = API_BASE + path
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    if method == "GET":
        r = requests.get(url, headers=headers, params=params, timeout=30)
    elif method == "POST":
        # POST 用 search/query 时，body 跟 query string 分开
        body = params.pop("body", None)
        r = requests.post(url, headers=headers, params=params, json=body, timeout=30)
    else:
        raise ValueError(f"unsupported method: {method}")
    r.raise_for_status()
    return r.json()


def list_sites() -> list[dict]:
    """列出所有已授权的 GSC sites。"""
    data = call("GET", "/sites")
    return data.get("siteEntry", [])


if __name__ == "__main__":
    print("== GSC 已授权的 sites ==")
    for s in list_sites():
        print(f"  {s['siteUrl']:50s}  perm={s['permissionLevel']}")

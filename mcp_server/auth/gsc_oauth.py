"""GSC OAuth 一次性授权脚本。

作用：
- 你 (user) 一次性运行，浏览器跳转 Google 登录并授权 Search Console 读权限
- 回调到本机的 http://localhost:8765
- 拿到 code 后换 access_token + refresh_token
- 把 refresh_token 存到 /home/ubuntu/notes/_work/gsc_token.json
- 之后所有 GSC API 调用都用 refresh_token 静默换 access_token，**不需要再授权**

注意：
- access_token 1 小时过期，每次用 refresh_token 静默换
- refresh_token 长期有效（除非用户撤销或长期不用）
- **GSC 必须用 OAuth 用户授权**（不能用 Service Account JSON key）
"""
import json
import os
import sys
import webbrowser
import secrets
import hashlib
import base64
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

ENV_FILE = os.path.expanduser("~/.hermes/.env")


def load_env():
    """从 ~/.hermes/.env 读 GSC 凭证。无 fallback。"""
    if not os.path.exists(ENV_FILE):
        sys.exit(f"找不到 {ENV_FILE}。请先创建并写入 GSC_CLIENT_ID / GSC_CLIENT_SECRET")
    env = {}
    for line in Path(ENV_FILE).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


ENV = load_env()
CLIENT_ID = ENV["GSC_CLIENT_ID"]
CLIENT_SECRET = ENV["GSC_CLIENT_SECRET"]
REDIRECT_URI = ENV.get("GSC_REDIRECT_URI", "http://localhost:8765")
SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
TOKEN_FILE = os.path.expanduser("~/.hermes/gsc_token.json")


# ---- PKCE (防 CSRF + 防 secret 泄露) ----
def make_pkce_pair():
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(
        hashlib.sha256(verifier.encode()).digest()
    ).rstrip(b"=").decode()
    return verifier, challenge


# ---- 授权 URL ----
def build_auth_url(state: str, challenge: str) -> str:
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",      # 关键：要求返回 refresh_token
        "prompt": "consent",          # 关键：每次都强制同意，否则不会给 refresh_token
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)


# ---- 接收回调 ----
class CallbackHandler(BaseHTTPRequestHandler):
    captured_code = None
    captured_state = None
    error = None

    def do_GET(self):
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if "error" in qs:
            self.error = qs["error"][0]
            self.send_response(400)
            self.end_headers()
            self.wfile.write(f"授权失败: {self.error}".encode())
            return
        self.captured_code = qs.get("code", [None])[0]
        self.captured_state = qs.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write("""
        <h2>✅ 授权成功！</h2>
        <p>可以关闭这个窗口，回到终端看输出。</p>
        """.encode())

    def log_message(self, *a, **kw):  # 静音
        pass


# ---- 用 code 换 token ----
def exchange_code_for_token(code: str, verifier: str) -> dict:
    import requests
    resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier,
        },
        timeout=30,
    )
    if resp.status_code != 200:
        sys.exit(f"换 token 失败: {resp.status_code} {resp.text}")
    return resp.json()


def main():
    state = secrets.token_urlsafe(16)
    verifier, challenge = make_pkce_pair()

    auth_url = build_auth_url(state, challenge)
    print(f"\n🌐 打开浏览器授权（如果没自动打开，请手动复制下面 URL）:\n\n{auth_url}\n")

    # 启动本地 HTTP server 等回调
    server = HTTPServer(("127.0.0.1", 8765), CallbackHandler)
    webbrowser.open(auth_url)
    print("⏳ 等待你在浏览器里点「允许」...")
    while CallbackHandler.captured_code is None and CallbackHandler.error is None:
        server.handle_request()

    if CallbackHandler.error:
        sys.exit(f"\n❌ 授权失败: {CallbackHandler.error}")
    if CallbackHandler.captured_state != state:
        sys.exit("\n❌ state 不匹配，可能被 CSRF 攻击，拒绝继续")

    print("\n✅ 拿到授权码，正在换 access_token + refresh_token...")
    tokens = exchange_code_for_token(CallbackHandler.captured_code, verifier)

    if "refresh_token" not in tokens:
        sys.exit("""
❌ Google 没返回 refresh_token。
可能原因：你之前已经授权过这个 app，再次授权 Google 不会给新 refresh_token。
解决：去 https://myaccount.google.com/permissions 找到这个 app → 撤销 → 重跑本脚本。
""")

    # 存盘
    save_data = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens["refresh_token"],
        "expires_in": tokens.get("expires_in", 3600),
        "scope": tokens.get("scope"),
        "token_type": tokens.get("token_type", "Bearer"),
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,  # 存了但用 PKCE 流程的话不需要
    }
    Path(TOKEN_FILE).write_text(json.dumps(save_data, indent=2, ensure_ascii=False))
    os.chmod(TOKEN_FILE, 0o600)
    print(f"\n✅ 授权完成！token 已存到:\n   {TOKEN_FILE}\n")
    print("接下来可以：")
    print("  1. 跑 mcp_server 跑通（python mcp_server/server.py）")
    print("  2. 调 mcp_server/tools/gsc.py 里的 top_queries() 验证")


if __name__ == "__main__":
    main()

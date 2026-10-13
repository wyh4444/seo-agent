"""GSC client 测试 — 覆盖 .env 加载 + token 加载。

不连真实 API（需要 OAuth），只测：
- .env 路径处理
- 字段校验
"""
import os
import pytest
import tempfile


def test_load_env_success(tmp_path):
    """有 .env 时正确加载。"""
    from mcp_server.gsc_client import _load_env
    env_file = tmp_path / ".env"
    env_file.write_text(
        "GSC_CLIENT_ID=test_id\n"
        "GSC_CLIENT_SECRET=test_secret\n"
        "GSC_REDIRECT_URI=http://localhost:8765\n"
    )
    # patch
    import mcp_server.gsc_client as gc
    orig = gc.ENV_FILE
    gc.ENV_FILE = str(env_file)
    try:
        env = gc._load_env()
        assert env["GSC_CLIENT_ID"] == "test_id"
        assert env["GSC_CLIENT_SECRET"] == "test_secret"
    finally:
        gc.ENV_FILE = orig


def test_load_env_missing_file(tmp_path):
    """无 .env 时 raise。"""
    import mcp_server.gsc_client as gc
    orig = gc.ENV_FILE
    gc.ENV_FILE = str(tmp_path / "nonexistent.env")
    try:
        with pytest.raises(FileNotFoundError):
            gc._load_env()
    finally:
        gc.ENV_FILE = orig


def test_load_env_missing_fields(tmp_path):
    """有 .env 但缺字段时 raise。"""
    import mcp_server.gsc_client as gc
    env_file = tmp_path / ".env"
    env_file.write_text("# 注释\nFOO=bar\n")
    orig = gc.ENV_FILE
    gc.ENV_FILE = str(env_file)
    try:
        with pytest.raises(ValueError, match="缺少字段"):
            gc._load_env()
    finally:
        gc.ENV_FILE = orig


def test_load_env_skips_comments_and_blanks(tmp_path):
    """注释和空行被跳过。"""
    import mcp_server.gsc_client as gc
    env_file = tmp_path / ".env"
    env_file.write_text(
        "# 注释\n"
        "\n"
        "GSC_CLIENT_ID=x\n"
        "GSC_CLIENT_SECRET=y\n"
        "  \n"
        "GSC_REDIRECT_URI=http://localhost:8765\n"
    )
    orig = gc.ENV_FILE
    gc.ENV_FILE = str(env_file)
    try:
        env = gc._load_env()
        assert "FOO" not in env
        assert env["GSC_CLIENT_ID"] == "x"
    finally:
        gc.ENV_FILE = orig


def test_load_token_missing_file(tmp_path):
    """无 token 文件时 raise。"""
    from mcp_server.gsc_client import _load_token
    import mcp_server.gsc_client as gc
    orig = gc.TOKEN_FILE
    gc.TOKEN_FILE = str(tmp_path / "nope.json")
    try:
        with pytest.raises(FileNotFoundError):
            gc._load_token()
    finally:
        gc.TOKEN_FILE = orig

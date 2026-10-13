"""pytest 配置文件"""
import sys
import os
from pathlib import Path

# 让 tests/ 能 import mcp_server
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

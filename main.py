#!/usr/bin/env python3
"""
🤖 Agent Workflow 主入口
使用AutoGen搭建Agent Workflow并实现全方位可观测性
"""

import sys
import os

# 确保src目录在Python路径中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    from src.demo import app
    app() 
"""导购 Agent：商品推荐。

调用商品检索工具（MCP 协议），生成推荐话术。
生产环境替换为三级 RAG 检索（见 three-stage-rag-kit 仓库）。
"""
from __future__ import annotations

from tools.mcp_tools import call_tool


def shopping_node(state: dict) -> dict:
    query = state.get("user_input", "")
    result = call_tool("recommend_product", {"query": query})
    answer = result.get("content", "暂无合适的商品推荐，请补充更多需求。")
    return {"messages": state["messages"] + [f"shopping_agent: {answer}"]}

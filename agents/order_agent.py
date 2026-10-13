"""订单 Agent：订单查询与物流跟踪。"""
from __future__ import annotations

from tools.mcp_tools import call_tool


def order_node(state: dict) -> dict:
    query = state.get("user_input", "")
    # 简单抽取订单号（生产用 NER）
    import re

    m = re.search(r"([A-Za-z0-9]{6,})", query)
    order_id = m.group(1) if m else "unknown"
    result = call_tool("query_order", {"order_id": order_id})
    answer = result.get("content", f"抱歉，未查询到订单 {order_id} 的信息。")
    return {"messages": state["messages"] + [f"order_agent: {answer}"]}


def after_sale_node(state: dict) -> dict:
    query = state.get("user_input", "")
    result = call_tool("after_sale_service", {"query": query})
    answer = result.get("content", "已为您记录售后诉求，专员将在1小时内联系您。")
    return {"messages": state["messages"] + [f"after_sale_agent: {answer}"]}

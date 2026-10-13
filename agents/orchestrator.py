"""Orchestrator Agent：意图识别与任务分发。

根据用户输入分类路由到对应业务 Agent：
- shopping  → 导购Agent
- order     → 订单Agent
- after_sale→ 售后Agent
- general   → 直接回复

采用「规则初筛 + 大模型精分类」两级策略（无 key 时仅规则分类）。
"""
from __future__ import annotations

import re

SHOPPING_KEYWORDS = ["推荐", "买", "想要", "适合", "怎么样", "多少钱", "价格", "耳机", "衣服", "鞋", "商品"]
ORDER_KEYWORDS = ["订单", "发货", "物流", "快递", "到哪", "退款", "签收"]
AFTER_SALE_KEYWORDS = ["退换", "退货", "换货", "维修", "坏了", "质量问题", "售后", "投诉"]


def classify_intent(query: str) -> str:
    """规则初筛意图分类。"""
    q = query.lower()
    if any(k in q for k in ORDER_KEYWORDS):
        return "order"
    if any(k in q for k in AFTER_SALE_KEYWORDS):
        return "after_sale"
    if any(k in q for k in SHOPPING_KEYWORDS):
        return "shopping"
    return "general"


def orchestrator_node(state: dict) -> dict:
    """LangGraph 节点：解析用户输入，写入意图与路由。"""
    query = state.get("user_input", "")
    intent = classify_intent(query)
    return {
        "intent": intent,
        "route": intent,
        "messages": state.get("messages", []) + [f"user: {query}"],
    }

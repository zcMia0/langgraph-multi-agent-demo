"""LangGraph StateGraph 编排：四层主从多 Agent 主流程。

节点链路：
user_input → orchestrator(路由) → 业务Agent(shopping/order/after_sale)
          → compliance(双路校验) → respond(输出 / 拦截 / 转人工)

三条边上的容错：
- 工具失败：tools 层重试→降级→转人工
- 合规拦截：回复被替换为合规话术
- 图执行异常：catch 兜底转人工
"""
from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from agents.orchestrator import orchestrator_node
from agents.shopping_agent import shopping_node
from agents.order_agent import after_sale_node, order_node
from compliance.rule_engine import rule_check
from compliance.semantic_check import semantic_check


class AgentState(TypedDict):
    user_input: str
    messages: list
    intent: str
    route: str
    answer: str
    blocked: bool
    block_reason: str


def compliance_node(state: AgentState) -> dict:
    """双路合规校验：规则引擎前置 + LLM 语义审核。"""
    answer = state.get("answer", "")
    rule_res = rule_check(answer)
    if rule_res["blocked"]:
        return {"blocked": True, "block_reason": "规则命中:" + ",".join(rule_res["hits"])}
    sem_res = semantic_check(answer)
    if sem_res.get("blocked"):
        return {"blocked": True, "block_reason": sem_res.get("reason", "semantic")}
    return {"blocked": False, "block_reason": ""}


def respond_node(state: AgentState) -> dict:
    """汇总最终回答：未拦截直接输出；拦截则替换为合规话术。"""
    messages = state["messages"]
    if state.get("blocked"):
        safe_reply = "抱歉，该回复因不符合平台合规要求已被拦截，客服将为您人工解答。"
        messages = messages + [f"compliance: {safe_reply}"]
        return {"messages": messages, "answer": safe_reply}
    answer = messages[-1].split(": ", 1)[-1] if messages else ""
    return {"answer": answer}


def build_graph():
    g = StateGraph(AgentState)

    g.add_node("orchestrator", orchestrator_node)
    g.add_node("shopping", shopping_node)
    g.add_node("order", order_node)
    g.add_node("after_sale", after_sale_node)
    g.add_node("compliance", compliance_node)
    g.add_node("respond", respond_node)

    g.set_entry_point("orchestrator")
    g.add_conditional_edges(
        "orchestrator",
        lambda s: s.get("route", "general"),
        {"shopping": "shopping", "order": "order", "after_sale": "after_sale", "general": "respond"},
    )
    g.add_edge("shopping", "compliance")
    g.add_edge("order", "compliance")
    g.add_edge("after_sale", "compliance")
    g.add_edge("compliance", "respond")
    g.add_edge("respond", END)

    return g.compile()


def run_graph(user_input: str) -> dict:
    """带异常兜底的图执行入口。"""
    graph = build_graph()
    try:
        return graph.invoke({"user_input": user_input, "messages": []})
    except Exception as e:  # noqa: BLE001
        return {
            "user_input": user_input,
            "answer": f"系统繁忙，已转人工处理（{e}）",
            "blocked": False,
            "messages": [],
        }

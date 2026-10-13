"""MCP 工具集：标准化工具注册与调用，内置三级容错（重试→降级→转人工）。

生产环境通过 MCP 协议对接外部系统（ERP/OMS/库存），
此处为可运行的最小实现，模拟工具注册表与调用链路。
"""
from __future__ import annotations

import time
from typing import Callable, Dict

# 工具注册表
_TOOL_REGISTRY: Dict[str, Callable] = {}

# 模拟的"外部系统"数据
_MOCK_DB = {
    "12345": {"status": "已发货", "carrier": "顺丰", "eta": "明天到达"},
    "67890": {"status": "待发货", "carrier": "-", "eta": "-"},
}
_MOCK_CATALOG = {
    "蓝牙耳机": "SonicPro 无线蓝牙耳机 主动降噪 长续航30小时 ¥299",
    "防晒衣": "夏日冰丝防晒衣 UPF50+ 大码 ¥159",
    "连衣裙": "夏季碎花连衣裙 宽松显瘦 度假风 ¥189",
}


def _query_order(args: dict) -> dict:
    order_id = args.get("order_id", "")
    info = _MOCK_DB.get(order_id)
    if info is None:
        return {"content": f"未查询到订单 {order_id}，请核对订单号。"}
    return {"content": f"订单 {order_id} 状态：{info['status']}（{info['carrier']}，{info['eta']}）"}


def _recommend_product(args: dict) -> dict:
    query = args.get("query", "")
    for key, desc in _MOCK_CATALOG.items():
        if key in query:
            return {"content": f"为您推荐：{desc}"}
    return {"content": "根据您的需求，推荐查看热门榜单商品。"}


def _after_sale_service(args: dict) -> dict:
    return {"content": "已记录售后诉求：{q}，专员将在1小时内联系您。".format(q=args.get("query", ""))}


def register_tool(name: str, fn: Callable) -> None:
    _TOOL_REGISTRY[name] = fn


def call_tool(name: str, args: dict, max_retries: int = 3) -> dict:
    """带容错的工具调用：重试 → 降级 → 转人工。"""
    fn = _TOOL_REGISTRY.get(name)
    if fn is None:
        return {"content": "系统繁忙，请稍后再试（工具不可用，已转人工处理）。", "fallback": "human"}

    for attempt in range(1, max_retries + 1):
        try:
            return fn(args)
        except Exception as e:  # noqa: BLE001
            if attempt == max_retries:
                # 降级：返回兜底文案
                return {
                    "content": f"服务暂时不可用（{e}），已为您记录问题，客服将尽快跟进。",
                    "fallback": "human",
                }
            time.sleep(0.3 * attempt)  # 指数退避
    return {"content": "系统繁忙，请稍后再试。", "fallback": "human"}


# 注册内置工具
register_tool("query_order", _query_order)
register_tool("recommend_product", _recommend_product)
register_tool("after_sale_service", _after_sale_service)

"""CLI 演示脚本：展示意图路由、双路合规拦截与容错链路。

用法：python examples/chat_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.state_graph import run_graph

TEST_CASES = [
    ("商品咨询", "帮我推荐一款无线蓝牙耳机"),
    ("订单查询", "我的订单12345发货了吗"),
    ("售后", "刚买的手机坏了想退货"),
    ("违规话术", "这款产品是全网最低价，绝对第一"),
]


def main():
    print("=" * 60)
    print("LangGraph Multi-Agent Demo（四层主从架构）")
    print("=" * 60)
    for name, query in TEST_CASES:
        print(f"\n【{name}】{query}")
        result = run_graph(query)
        print(f"意图路由: {result.get('intent', '-')}")
        if result.get("blocked"):
            print(f"合规校验: 已拦截（{result.get('block_reason')}）")
        print(f"最终回复: {result.get('answer', '')}")

    print("\n" + "=" * 60)
    print("进入交互模式（输入 q 退出）")
    while True:
        query = input("\n用户: ").strip()
        if query.lower() in ("q", "quit", "退出"):
            break
        result = run_graph(query)
        print(f"回复: {result.get('answer', '')}")


if __name__ == "__main__":
    main()

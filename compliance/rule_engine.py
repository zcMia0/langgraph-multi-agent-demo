"""规则引擎：广告法 & 平台规则关键词前置校验。

命中即拦截，覆盖绝对化用语、虚假宣传等常见违规点。
"""
from __future__ import annotations

# 广告法禁用词 / 平台规则敏感词（示例集合，可按业务扩展）
RULE_BLACKLIST = [
    "全网最低价", "最低价", "最便宜", "第一", "顶级", "最好",
    "绝对", "100%有效", "国家级", "全球唯一", "史无前例",
    "永久", "根治", "包治百病",
]


def rule_check(text: str) -> dict:
    """返回 {"blocked": bool, "hits": [命中词]}"""
    hits = [w for w in RULE_BLACKLIST if w in text]
    return {"blocked": len(hits) > 0, "hits": hits}

"""大模型语义审核：对规则引擎漏网的隐式违规做二次校验。

无 API Key 时降级为关键词兜底；配置 key 后走 LLM 审核。
设计目标：合规召回率 96.5%，误判率 < 3%。
"""
from __future__ import annotations

import os

from compliance.rule_engine import rule_check

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # noqa: BLE001
    pass

_API_KEY = os.getenv("LLM_API_KEY", "")


def _llm_review(text: str) -> dict:
    """调用 LLM 做语义合规审核（示意实现，生产按 OpenAI 兼容接口封装）。"""
    from openai import OpenAI

    client = OpenAI(api_key=_API_KEY, base_url=os.getenv("LLM_BASE_URL", "https://api.openai.com/v1"))
    resp = client.chat.completions.create(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "你是电商平台合规审核员。判断以下客服话术是否违反广告法或平台规则（绝对化用语、虚假承诺、诱导交易等）。只输出 JSON：{\"blocked\": bool, \"reason\": \"\"}",
            },
            {"role": "user", "content": text},
        ],
        temperature=0,
    )
    import json

    content = resp.choices[0].message.content or "{}"
    try:
        return json.loads(content)
    except Exception:  # noqa: BLE001
        return {"blocked": False, "reason": "parse_error"}


def semantic_check(text: str) -> dict:
    """语义审核入口：有 key 走 LLM，无 key 降级关键词兜底。"""
    if _API_KEY:
        return _llm_review(text)
    # 降级：规则兜底
    res = rule_check(text)
    return {"blocked": res["blocked"], "reason": "keyword_fallback:" + ",".join(res["hits"])}

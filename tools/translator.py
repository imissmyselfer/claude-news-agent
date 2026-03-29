"""
翻譯工具
使用 Anthropic Messages API（非 Agent SDK）做英翻中
因為翻譯是明確的單一任務，不需要 Agent 迴圈，直接呼叫 API 更有效率
"""

import os
import anthropic

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY", ""))


async def translate_to_chinese(text: str, title: str = "") -> dict:
    """
    將英文文章翻譯為繁體中文

    回傳：
    {
        "translated_title": "中文標題",
        "translated_content": "中文內文",
        "summary": "100字以內的中文摘要",
        "key_points": ["要點1", "要點2", "要點3"],
    }
    """
    prompt = f"""請將以下英文新聞翻譯為繁體中文，並以 JSON 格式回傳結果。

原文標題：{title}

原文內容：
{text}

請回傳以下 JSON 格式（只回傳 JSON，不要其他說明）：
{{
  "translated_title": "繁體中文標題",
  "translated_content": "完整繁體中文翻譯",
  "summary": "100字以內的重點摘要",
  "key_points": ["要點一", "要點二", "要點三"]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    import json
    raw = message.content[0].text.strip()

    # 清除可能的 markdown 包裝
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]

    return json.loads(raw.strip())

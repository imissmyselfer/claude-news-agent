"""
文章發布工具
將整理好的新聞輸出為 Hugo/Eleventy 相容的 Markdown 檔案
"""

import os
import re
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "posts"


def _slugify(title: str) -> str:
    """將標題轉為 URL 友好的 slug"""
    # 移除非字母數字字符，空格換成 dash
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = slug.strip("-")
    # 如果是中文標題，改用日期+隨機碼
    if not slug or not any(c.isascii() and c.isalpha() for c in slug):
        slug = datetime.now().strftime("%H%M%S")
    return slug[:60]


async def publish_article(
    title: str,
    content: str,
    category: str = "general",
    source_url: str = "",
) -> str:
    """
    將文章輸出為 Markdown 檔案

    檔案格式相容 Hugo front matter，
    也適用於 Eleventy、Jekyll 等靜態網站框架

    回傳：輸出的檔案路徑
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    slug = _slugify(title)
    filename = f"{date_str}-{slug}.md"
    filepath = OUTPUT_DIR / filename

    # Hugo / Eleventy 相容的 front matter
    front_matter = f"""---
title: "{title}"
date: {now.strftime("%Y-%m-%dT%H:%M:%S+08:00")}
category: "{category}"
draft: false
source_url: "{source_url}"
---
"""

    full_content = front_matter + "\n" + content

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)

    print(f"📄 已寫入：{filepath}")
    return str(filepath)

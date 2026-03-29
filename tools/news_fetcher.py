"""
新聞抓取工具
使用 NewsAPI 免費方案取得當日國際與科技新聞
免費方案：每月 1,000 次請求，適合個人每日使用
申請 API Key：https://newsapi.org/register
"""

import os
import aiohttp
from datetime import date
from typing import Literal

NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "")
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# NewsAPI 免費方案支援的來源
SOURCES = {
    "international": "bbc-news,reuters,associated-press,the-guardian-uk",
    "technology": "techcrunch,the-verge,wired,ars-technica",
    "all": "bbc-news,reuters,techcrunch,the-verge",
}


async def fetch_top_news(
    category: Literal["international", "technology", "all"] = "all",
    max_count: int = 5,
) -> list[dict]:
    """
    從 NewsAPI 取得最新新聞

    回傳格式：
    [
        {
            "title": "文章標題",
            "description": "摘要",
            "url": "原文連結",
            "source": "來源名稱",
            "published_at": "發布時間",
        },
        ...
    ]
    """
    if not NEWS_API_KEY:
        raise EnvironmentError("請設定環境變數 NEWS_API_KEY")

    sources = SOURCES.get(category, SOURCES["all"])

    params = {
        "sources": sources,
        "pageSize": max_count,
        "apiKey": NEWS_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(NEWS_API_URL, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title", ""),
            "description": item.get("description", ""),
            "url": item.get("url", ""),
            "source": item.get("source", {}).get("name", "Unknown"),
            "published_at": item.get("publishedAt", ""),
            "content_preview": item.get("content", "")[:500],  # NewsAPI 免費版只給前 200 字
        })

    return articles

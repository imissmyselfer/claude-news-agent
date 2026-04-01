"""
新聞抓取工具
使用 NewsAPI 免費方案取得當日國際與科技新聞
免費方案：每月 1,000 次請求，適合個人每日使用
申請 API Key：https://newsapi.org/register
"""

import os
import aiohttp
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
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

LOCAL_RSS_FEEDS = [
    ("Palo Alto Online", "https://paloaltoonline.com/feed/"),
    ("Mountain View Voice", "https://www.mv-voice.com/feed/"),
]

LOS_ALTOS_URL = "https://www.losaltosonline.com"


async def fetch_top_news(
    category: Literal["international", "technology", "all", "local"] = "all",
    max_count: int = 5,
) -> list[dict]:
    """
    從 NewsAPI 取得最新新聞（或本地新聞來源）

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
    if category == "local":
        return await fetch_local_news(max_count)

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


async def fetch_local_news(max_count: int = 3) -> list[dict]:
    """
    抓取 Los Altos、Mountain View、Palo Alto 本地新聞
    - Palo Alto Online 和 Mountain View Voice：RSS feed
    - Los Altos Town Crier：爬首頁文章連結
    """
    results = []
    timeout = aiohttp.ClientTimeout(total=15)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        # RSS feeds
        for source_name, feed_url in LOCAL_RSS_FEEDS:
            try:
                async with session.get(feed_url) as resp:
                    resp.raise_for_status()
                    text = await resp.text()

                root = ET.fromstring(text)
                channel = root.find("channel")
                items = channel.findall("item") if channel is not None else []

                for item in items[:max_count]:
                    title = (item.findtext("title") or "").strip()
                    url = (item.findtext("link") or "").strip()
                    description = (item.findtext("description") or "").strip()
                    pub_date = (item.findtext("pubDate") or "").strip()
                    if title and url:
                        results.append({
                            "title": title,
                            "description": description[:300],
                            "url": url,
                            "source": source_name,
                            "published_at": pub_date,
                            "content_preview": "",
                        })
            except Exception:
                pass

        # Los Altos Town Crier — scrape homepage
        try:
            async with session.get(LOS_ALTOS_URL) as resp:
                resp.raise_for_status()
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")
            seen_urls = set()
            for a in soup.select("a[href]"):
                href = a.get("href", "")
                if "/article_" in href and href.endswith(".html"):
                    if not href.startswith("http"):
                        href = LOS_ALTOS_URL + href
                    if href in seen_urls:
                        continue
                    seen_urls.add(href)
                    title = a.get_text(strip=True)
                    if len(title) > 10:
                        results.append({
                            "title": title,
                            "description": "",
                            "url": href,
                            "source": "Los Altos Town Crier",
                            "published_at": "",
                            "content_preview": "",
                        })
                    if len(seen_urls) >= max_count:
                        break
        except Exception:
            pass

    return results

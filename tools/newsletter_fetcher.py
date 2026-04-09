"""
新聞電子報抓取工具
從 TLDR Newsletter、1440 Daily Digest、The Rundown AI 抓取最新內容
"""

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from datetime import date, timedelta
from typing import Literal


async def fetch_tldr_newsletter(max_count: int = 3) -> list[dict]:
    """
    抓取 TLDR Newsletter 最新科技與 AI 內容
    https://tldr.tech/{category}/{YYYY-MM-DD}
    """
    results = []
    today = date.today().strftime("%Y-%m-%d")
    categories = ["tech", "ai"]

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PersonalNewsBot/1.0)"
    }

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        for category in categories:
            url = f"https://tldr.tech/{category}/{today}"
            try:
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    html = await resp.text()

                soup = BeautifulSoup(html, "html.parser")

                # TLDR 頁面結構：section > article
                articles = soup.select("section article")

                for article in articles[:max_count]:
                    # 提取標題
                    title_tag = article.select_one("h3") or article.select_one("h2")
                    if not title_tag:
                        continue
                    title = title_tag.get_text(strip=True)
                    if not title:
                        continue

                    # 提取連結
                    link_tag = article.select_one("a[href]")
                    link = link_tag.get("href", "") if link_tag else ""
                    if not link:
                        continue
                    # 清除 utm 參數
                    if "?" in link:
                        link = link.split("?")[0]

                    # 提取摘要（嘗試多個選擇器）
                    summary = ""
                    summary_tag = article.select_one("div.newsletter-html") or \
                                  article.select_one("p") or \
                                  article.select_one(".description")
                    if summary_tag:
                        summary = summary_tag.get_text(strip=True)[:300]

                    results.append({
                        "title": title,
                        "description": summary,
                        "url": link,
                        "source": f"TLDR Newsletter ({category.upper()})",
                        "published_at": today,
                        "content_preview": "",
                    })

                    if len(results) >= max_count:
                        break

            except Exception as e:
                # 靜默失敗（該日期可能無內容）
                pass

    return results


async def fetch_1440_digest(max_count: int = 3) -> list[dict]:
    """
    抓取 1440 Daily Digest 最新國際新聞
    https://join1440.com/today
    """
    results = []
    url = "https://join1440.com/today"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PersonalNewsBot/1.0)"
    }

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        try:
            async with session.get(url, headers=headers) as resp:
                resp.raise_for_status()
                html = await resp.text()

            soup = BeautifulSoup(html, "html.parser")

            # 1440 內容為 email HTML 表格格式
            # 提取所有連結與相關的文字內容
            links = soup.select('a[style*="color"][href]')

            seen_urls = set()
            for link in links:
                href = link.get("href", "").strip()
                if not href or href in seen_urls:
                    continue
                if href.startswith("http"):
                    # 提取連結文字作為標題
                    title = link.get_text(strip=True)
                    if title and len(title) > 5:  # 過濾太短的文字
                        seen_urls.add(href)
                        results.append({
                            "title": title,
                            "description": "",  # 1440 結構中難以提取摘要
                            "url": href,
                            "source": "1440 Daily Digest",
                            "published_at": date.today().strftime("%Y-%m-%d"),
                            "content_preview": "",
                        })

                        if len(results) >= max_count:
                            break

        except Exception as e:
            # 靜默失敗
            pass

    return results


async def fetch_rundown_ai(max_count: int = 3) -> list[dict]:
    """
    抓取 The Rundown AI 最新 AI 新聞
    https://therundown.ai

    注：該網站為 Vite SPA（純 JavaScript 渲染），
    BeautifulSoup 無法獲取動態渲染的內容。
    嘗試備用存檔 URL 格式（Beehiiv 平台），失敗則優雅降級。
    """
    results = []
    today = date.today().strftime("%Y-%m-%d")

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PersonalNewsBot/1.0)"
    }

    timeout = aiohttp.ClientTimeout(total=15)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        # 嘗試主站
        try:
            async with session.get("https://therundown.ai", headers=headers, timeout=timeout) as resp:
                resp.raise_for_status()
                html = await resp.text()

            # 檢查是否獲得靜態內容（Vite SPA 會回傳空的 #app div）
            if len(html) > 5000:  # 合理大小表示有內容
                soup = BeautifulSoup(html, "html.parser")
                articles = soup.select("article, [role='article'], .article, .post")

                for article in articles[:max_count]:
                    title = article.select_one("h2, h3, a")
                    if title:
                        results.append({
                            "title": title.get_text(strip=True),
                            "description": "",
                            "url": "https://therundown.ai",
                            "source": "The Rundown AI",
                            "published_at": today,
                            "content_preview": "",
                        })

        except Exception:
            pass

        # 若主站失敗，嘗試備用存檔 URL（Beehiiv 平台）
        if not results:
            # Beehiiv 通常使用 /p/ 路徑，但無公開日期存檔
            # 或嘗試最近發布的文章
            try:
                async with session.get("https://therundown.ai/latest", headers=headers, timeout=timeout) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        soup = BeautifulSoup(html, "html.parser")
                        # 簡化的提取邏輯
                        titles = soup.select("h2, h3, a[href*='/p/']")
                        for title_tag in titles[:max_count]:
                            text = title_tag.get_text(strip=True)
                            if text and len(text) > 3:
                                results.append({
                                    "title": text,
                                    "description": "",
                                    "url": "https://therundown.ai",
                                    "source": "The Rundown AI",
                                    "published_at": today,
                                    "content_preview": "",
                                })
            except Exception:
                pass

    # 若所有嘗試都失敗，打印警告
    if not results:
        print("⚠️  The Rundown AI：無法抓取內容（網站使用 JS 渲染）")

    return results


async def fetch_newsletters(
    source: Literal["tldr", "1440", "rundown", "all"] = "all",
    max_count: int = 3,
) -> list[dict]:
    """
    統一入口：抓取新聞電子報

    :param source: "tldr" | "1440" | "rundown" | "all"
    :param max_count: 每個來源的最大文章數
    :return: 統一格式的文章列表
    """
    tasks = []

    if source in ("tldr", "all"):
        tasks.append(fetch_tldr_newsletter(max_count))
    if source in ("1440", "all"):
        tasks.append(fetch_1440_digest(max_count))
    if source in ("rundown", "all"):
        tasks.append(fetch_rundown_ai(max_count))

    results = await asyncio.gather(*tasks) if tasks else []

    # 扁平化結果
    all_articles = []
    for article_list in results:
        all_articles.extend(article_list)

    return all_articles

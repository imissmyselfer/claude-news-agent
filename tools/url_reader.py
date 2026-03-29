"""
URL 文章讀取工具
給定網址，抓取並解析文章主要內容（去除廣告、導航列等雜訊）
"""

import aiohttp
from bs4 import BeautifulSoup


async def read_article_from_url(url: str) -> str:
    """
    抓取指定 URL 的文章內容

    使用 BeautifulSoup 解析 HTML，
    優先提取 <article>、<main> 等語意標籤的內容
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (compatible; PersonalNewsBot/1.0)"
        )
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            resp.raise_for_status()
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

    # 移除無用標籤
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        tag.decompose()

    # 嘗試取得文章主體（依語意標籤優先順序）
    content_tag = (
        soup.find("article")
        or soup.find("main")
        or soup.find(class_=lambda c: c and any(
            kw in c.lower() for kw in ["article", "content", "post-body", "entry"]
        ))
        or soup.find("body")
    )

    if content_tag:
        # 取得純文字，保留段落換行
        paragraphs = content_tag.find_all(["p", "h1", "h2", "h3", "h4", "blockquote"])
        text = "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
    else:
        text = soup.get_text(separator="\n", strip=True)

    # 擷取標題
    title = ""
    if soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)
    elif soup.find("title"):
        title = soup.find("title").get_text(strip=True)

    return f"標題：{title}\n\n來源 URL：{url}\n\n內文：\n{text[:8000]}"  # 限制長度避免超過 context

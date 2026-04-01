import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import argparse
from datetime import datetime
from claude_agent_sdk import (
    tool, create_sdk_mcp_server,
    ClaudeAgentOptions, ClaudeSDKClient,
    AssistantMessage, TextBlock,
)

from tools.news_fetcher import fetch_top_news
from tools.url_reader import read_article_from_url
from tools.translator import translate_to_chinese
from tools.publisher import publish_article


# ─── Tool definitions ────────────────────────────────────────

@tool("fetch_news", "抓取當日重要國際與科技新聞列表", {
    "category": str,
    "max_count": int,
})
async def tool_fetch_news(args):
    articles = await fetch_top_news(
        category=args.get("category", "all"),
        max_count=args.get("max_count", 5),
    )
    return {"content": [{"type": "text", "text": str(articles)}]}


@tool("read_url", "從指定 URL 讀取文章完整內容", {
    "url": str,
})
async def tool_read_url(args):
    content = await read_article_from_url(args["url"])
    return {"content": [{"type": "text", "text": content}]}


@tool("translate", "將英文文章翻譯成繁體中文", {
    "text": str,
    "title": str,
})
async def tool_translate(args):
    result = await translate_to_chinese(
        text=args["text"],
        title=args.get("title", ""),
    )
    return {"content": [{"type": "text", "text": str(result)}]}


@tool("publish", "將整理好的文章發布成 Markdown 檔案", {
    "title": str,
    "content": str,
    "category": str,
    "source_url": str,
})
async def tool_publish(args):
    filepath = await publish_article(
        title=args["title"],
        content=args["content"],
        category=args.get("category", "general"),
        source_url=args.get("source_url", ""),
    )
    return {"content": [{"type": "text", "text": f"已發布：{filepath}"}]}


# ─── Agent runner ────────────────────────────────────────────

async def _run_agent(prompt: str):
    server = create_sdk_mcp_server(
        name="news-tools",
        version="1.0.0",
        tools=[tool_fetch_news, tool_read_url, tool_translate, tool_publish],
    )

    options = ClaudeAgentOptions(
        mcp_servers={"news-tools": server},   # ← dict, not list
        allowed_tools=[
            "mcp__news-tools__fetch_news",
            "mcp__news-tools__read_url",
            "mcp__news-tools__translate",
            "mcp__news-tools__publish",
        ],
        permission_mode="bypassPermissions",
    )

    print("🤖 Agent 啟動中...\n")
    async with ClaudeSDKClient(options=options) as client:
        await client.query(prompt=prompt)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
    print("\n✅ 完成！")


# ─── Modes ───────────────────────────────────────────────────

async def run_daily_digest():
    today = datetime.now().strftime("%Y-%m-%d")
    prompt = f"""
今天是 {today}，請完成每日新聞台的工作流程：
1. 使用 fetch_news 抓取 international 類別前 3 篇新聞
2. 使用 fetch_news 抓取 technology 類別前 3 篇新聞
3. 使用 fetch_news 抓取 local 類別前 3 篇新聞（Los Altos、Mountain View、Palo Alto 本地新聞）
4. 對每篇使用 read_url 讀取完整內容，再用 translate 翻譯成繁體中文
5. 使用 publish 發布每篇文章，注意：
   - title 填入中文標題
   - content 只包含來源、摘要與重點，不要再重複標題（Hugo 會自動顯示）
   - content 格式如下：
     **來源：** xxx｜**發布日期：** yyyy-mm-dd

     ---

     ### 📋 摘要
     （100字以內）

     ---

     ### 🔑 重點整理
     - 要點一
     - 要點二
     - 要點三
"""
    await _run_agent(prompt)


async def run_url_mode(url: str):
    prompt = f"""
請處理並發布這篇文章：
1. 使用 read_url 讀取：{url}
2. 若為英文，用 translate 翻譯成繁體中文
3. 判斷分類（international、technology 或 local）
4. 使用 publish 發布每篇文章，注意需要完整翻譯：
   - title 填入中文標題
   - content 只包含來源、摘要與重點，不要再重複標題（Hugo 會自動顯示）
   - content 格式如下：
     **來源：** xxx｜**發布日期：** yyyy-mm-dd

     ---

     ### 📋 摘要
     （100字以內）

     ---

     ### 🔑 重點整理
     - 要點一
     - 要點二
     - 要點三
"""
    await _run_agent(prompt)


# ─── Entry point ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="")
    args = parser.parse_args()

    if args.url:
        asyncio.run(run_url_mode(args.url))
    else:
        asyncio.run(run_daily_digest())

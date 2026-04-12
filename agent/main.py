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
from tools.publisher import publish_article
from tools.newsletter_fetcher import fetch_newsletters


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


@tool("fetch_newsletter", "抓取新聞電子報（TLDR Newsletter、1440 Daily Digest、The Rundown AI）", {
    "source": str,
    "max_count": int,
})
async def tool_fetch_newsletter(args):
    articles = await fetch_newsletters(
        source=args.get("source", "all"),
        max_count=args.get("max_count", 3),
    )
    return {"content": [{"type": "text", "text": str(articles)}]}


# ─── Agent runner ────────────────────────────────────────────

async def _run_agent(prompt: str):
    server = create_sdk_mcp_server(
        name="news-tools",
        version="1.0.0",
        tools=[tool_fetch_news, tool_publish, tool_fetch_newsletter],
    )

    # TODO: 待 Claude Agent SDK 支持 cache_control 參數後，
    # 在 ClaudeAgentOptions 中加入：
    #   cache_control={"type": "ephemeral"}
    # 這樣可以將系統 prompt（每日相同）的費用從 100% 降至 10%
    # 預期 Agent SDK v0.2.0+ 會支持此功能
    options = ClaudeAgentOptions(
        mcp_servers={"news-tools": server},   # ← dict, not list
        allowed_tools=[
            "mcp__news-tools__fetch_news",
            "mcp__news-tools__publish",
            "mcp__news-tools__fetch_newsletter",
            "web_fetch",  # ← 原生工具，自動可用
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

【第一部分：傳統新聞來源（NewsAPI）】
1. 使用 fetch_news 抓取 international 類別前 5 篇新聞
2. 使用 fetch_news 抓取 technology 類別前 5 篇新聞
3. 使用 fetch_news 抓取 local 類別前 3 篇新聞（Los Altos、Mountain View、Palo Alto 本地新聞）

【第二部分：新聞電子報（Newsletter）】
4. 使用 fetch_newsletter 抓取 tldr 電子報前 3 篇科技新聞（category: technology）
5. 使用 fetch_newsletter 抓取 1440 電子報前 3 篇國際新聞（category: international）
6. 使用 fetch_newsletter 抓取 rundown 電子報前 3 篇 AI 新聞（category: ai）

【第三部分：文章處理】
7. 對上述所有文章（共 9-18 篇），逐篇執行：
   a. 若有 URL，使用 web_fetch 讀取完整內容
   b. 分析文章內容，若為英文請翻譯成繁體中文（包含標題、摘要、重點整理都要翻譯）
   c. 使用 publish 發布每篇文章，注意：
      - title 填入中文標題（避免重複）
      - content 只包含來源、摘要與重點，不要再重複標題（Hugo 會自動顯示）
      - content 格式如下：
        **來源：** xxx｜**發布日期：** yyyy-mm-dd

        ---

        ### 📋 摘要
        （100字以內的中文摘要）

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
1. 使用 web_fetch 讀取：{url}
2. 分析文章內容，若為英文請翻譯成繁體中文（包含標題、摘要、重點整理都要翻譯）
3. 判斷分類（international、technology 或 local）
4. 使用 publish 發布文章，注意：
   - title 填入中文標題
   - content 只包含來源、摘要與重點，不要再重複標題（Hugo 會自動顯示）
   - content 格式如下：
     **來源：** xxx｜**發布日期：** yyyy-mm-dd

     ---

     ### 📋 摘要
     （100字以內的中文摘要）

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

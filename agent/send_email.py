#!/usr/bin/env python3
"""
每日新聞摘要 Email 寄送腳本
讀取當天發布的所有文章，整合成繁體中文摘要，透過 Gmail SMTP 寄送
"""

import os
import re
import sys
import re
import smtplib
import ssl
import argparse
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path


# 環境變數
GMAIL_USER = os.environ.get("GMAIL_USER", "").strip()
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "").strip()
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "").strip()

OUTPUT_DIR = Path(__file__).parent.parent / "output" / "posts"


def read_today_articles() -> list[dict]:
    """
    讀取今天發布的所有文章
    從 output/posts/{YYYY-MM-DD}-*.md 讀取並解析
    """
    today = date.today().strftime("%Y-%m-%d")
    articles = []

    if not OUTPUT_DIR.exists():
        return articles

    for file_path in sorted(OUTPUT_DIR.glob(f"{today}-*.md")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 解析 YAML front matter
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue

            front_matter = parts[1]
            body = parts[2].strip()

            # 提取 title 與 source_url
            title_match = re.search(r'title:\s*"([^"]*)"', front_matter)
            source_match = re.search(r'source_url:\s*"([^"]*)"', front_matter)

            title = title_match.group(1) if title_match else ""
            source_url = source_match.group(1) if source_match else ""

            # 提取摘要（### 📋 摘要 段落下的內容）
            summary = ""
            summary_match = re.search(r"###\s+📋\s+摘要\s*\n\n(.*?)(?:\n---|\n###|$)", body, re.DOTALL)
            if summary_match:
                summary = summary_match.group(1).strip()
                # 只取前 200 字
                if len(summary) > 200:
                    summary = summary[:200] + "..."
            else:
                # 若無摘要段落，取正文前 200 字
                summary = body[:200] + "..."

            if title:
                articles.append({
                    "title": title,
                    "summary": summary,
                    "source_url": source_url,
                    "file": file_path.name,
                })

        except Exception as e:
            print(f"⚠️  無法讀取 {file_path.name}: {e}")
            continue

    return articles


def build_email_html(articles: list[dict], today: str, label: str = "每日新聞摘要") -> str:
    """
    構建 HTML 格式的每日摘要 Email

    格式：
    - 標題欄（日期）
    - 文章列表（每篇：標題 + 摘要 + 原文連結）
    """
    if not articles:
        return """
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">📰 Bit Daily - """ + label + """</h1>
                <p style="color: #7f8c8d; margin-bottom: 20px;">發布日期：""" + today + """</p>
                <p style="color: #e74c3c; font-size: 16px;">今日無新文章發布。</p>
            </div>
        </body>
        </html>
        """

    articles_html = ""
    for i, article in enumerate(articles, 1):
        source_link = ""
        if article["source_url"]:
            source_link = f'<p style="margin-top: 10px;"><a href="{article["source_url"]}" style="color: #3498db; text-decoration: none;">🔗 查看原文</a></p>'

        article_html = f"""
        <div style="margin-bottom: 25px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #3498db; border-radius: 4px;">
            <h3 style="margin-top: 0; margin-bottom: 10px; color: #2c3e50;">{i}. {article["title"]}</h3>
            <p style="margin: 10px 0; color: #555; line-height: 1.6;">{article["summary"]}</p>
            {source_link}
        </div>
        """
        articles_html += article_html

    html = f"""
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; color: #333; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: white; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
            <h1 style="color: #2c3e50; margin-bottom: 5px;">📰 Bit Daily - {label}</h1>
            <p style="color: #7f8c8d; margin-bottom: 20px; font-size: 14px;">發布日期：{today}</p>
            <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
            {articles_html}
            <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
            <p style="color: #95a5a6; font-size: 12px; text-align: center;">
                由 <a href="https://claude-news-agent.netlify.app/" style="color: #3498db; text-decoration: none;">Claude News Agent</a> 自動生成
            </p>
        </div>
    </body>
    </html>
    """
    return html


def send_email(subject: str, html_body: str) -> bool:
    """
    透過 Gmail SMTP 寄送 Email
    使用 TLS 加密（smtp.gmail.com:465）

    :return: 寄送成功返回 True，失敗返回 False
    """
    try:
        # 建立 SSL context
        context = ssl.create_default_context()

        # 連線到 Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            # 登入
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)

            # 構建 Email
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = GMAIL_USER
            msg["To"] = RECIPIENT_EMAIL

            # 新增 HTML 內容
            html_part = MIMEText(html_body, "html", _charset="UTF-8")
            msg.attach(html_part)

            # 寄送
            server.sendmail(GMAIL_USER, RECIPIENT_EMAIL, msg.as_string())

        print(f"✅ Email 已寄出到 {RECIPIENT_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail 登入失敗：請檢查 GMAIL_USER 和 GMAIL_APP_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP 錯誤：{e}")
        return False
    except Exception as e:
        print(f"❌ 寄送 Email 時出錯：{e}")
        return False


def main():
    # 解析命令列參數
    parser = argparse.ArgumentParser(description="寄送每日新聞摘要 Email")
    parser.add_argument("--label", default="每日新聞摘要", help="Email 主旨標籤（預設：每日新聞摘要）")
    args = parser.parse_args()

    # 檢查環境變數
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not RECIPIENT_EMAIL:
        print("⚠️  未設定完整的 Email 環境變數")
        print(f"   GMAIL_USER: {bool(GMAIL_USER)}")
        print(f"   GMAIL_APP_PASSWORD: {bool(GMAIL_APP_PASSWORD)}")
        print(f"   RECIPIENT_EMAIL: {bool(RECIPIENT_EMAIL)}")
        print("\n   跳過 Email 寄送步驟。")
        return 0

    today = date.today().strftime("%Y-%m-%d")

    # 判斷是 pipe 輸入還是讀檔案
    if not sys.stdin.isatty():
        # 從 pipe 接收 claude 輸出
        print("📥 從 pipe 接收內容...")
        content = sys.stdin.read().strip()
        # 清掉 markdown code block
        content = re.sub(r'^```html\s*', '', content, flags=re.MULTILINE)
        content = re.sub(r'^```\s*$', '', content, flags=re.MULTILINE)
        html_body = f"""
        <html>
        <head><meta charset="UTF-8"></head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #333; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: white; border-radius: 8px;">
                <h1 style="color: #2c3e50;">📰 Bit Daily - {args.label}</h1>
                <p style="color: #7f8c8d; font-size: 14px;">發布日期：{today}</p>
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                <div style="line-height: 1.8;">{content}</div>
                <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 20px 0;">
                <p style="color: #95a5a6; font-size: 12px; text-align: center;">由 Bit Daily 自動生成</p>
            </div>
        </body>
        </html>
        """
    else:
        # 原本的邏輯：讀取 output/posts/ 裡的檔案
        articles = read_today_articles()
        print(f"📄 找到 {len(articles)} 篇今日文章")
        html_body = build_email_html(articles, today, args.label)

    subject = f"📰 Bit Daily - {today} {args.label}"
    success = send_email(subject, html_body)
    return 0 if success else 1
    
if __name__ == "__main__":
    sys.exit(main())

# 📰 Bit Daily 升級指南

本文檔說明 2026-04-09 的升級改動。

---

## 🆕 新增功能

### 1️⃣ 電子報來源抓取

除了現有的 NewsAPI 國際/科技/本地新聞，現已新增三個電子報來源：

| 電子報 | 來源 | 分類 | 說明 |
|-------|------|------|------|
| **TLDR Newsletter** | https://tldr.tech | technology / ai | 每日科技 + AI 新聞 |
| **1440 Daily Digest** | https://join1440.com | international | 國際綜合新聞 |
| **The Rundown AI** | https://therundown.ai | ai | AI 相關專項 |

**實現方式**：
- 新建 `tools/newsletter_fetcher.py`，包含三個爬蟲函數
- TLDR Newsletter 和 1440 可正常抓取
- The Rundown AI 因使用 JavaScript SPA 架構無法直接爬取，會優雅降級（返回空列表 + 警告資訊）

### 2️⃣ 每日 Email 摘要寄送

GitHub Actions 執行完畢後，自動寄送當日新聞摘要 Email。

**實現方式**：
- 新建 `agent/send_email.py`，使用 Gmail SMTP（Python 內建 `smtplib`）
- 讀取 `output/posts/` 中當天的 Markdown 文章
- 解析 front matter 和摘要段落
- 生成 HTML 格式的 Email
- 透過 `smtp.gmail.com:465` 寄送

---

## 📝 修改清單

### 新建文件

```
tools/newsletter_fetcher.py       (267 行) — 電子報爬蟲
agent/send_email.py               (241 行) — Email 寄送腳本
```

### 修改文件

```
agent/main.py                     (+ 23 行) — 新增 fetch_newsletter 工具
.github/workflows/daily-news.yml  (+ 7 行)  — 新增 Email 寄送步驟
.env.example                      (+ 5 行)  — 新增 Email 環境變數
README.md                         (+ 50 行) — 更新文檔，說明新功能
```

---

## ⚙️ 配置步驟

### 步驟 1：更新本地環境變數（可選，用於本地測試）

```bash
cp .env.example .env
nano .env
# 新增三個 Gmail 相關的環境變數（可先留空，使用時再填）
```

### 步驟 2：配置 GitHub Secrets（重要）

1. 前往你的 GitHub Repo
2. **Settings** → **Secrets and variables** → **Actions**
3. 點擊 **New repository secret**，新增以下內容：

#### 原有 Secrets（確保已設定）：
- `ANTHROPIC_API_KEY`: 你的 Anthropic API Key
- `NEWS_API_KEY`: 你的 NewsAPI Key

#### 新增 Secrets（用於 Email）：
- `GMAIL_USER`: 你的 Gmail 信箱（如 `your-email@gmail.com`）
- `GMAIL_APP_PASSWORD`: Gmail 應用程式專用密碼（16 位數字）
- `RECIPIENT_EMAIL`: 接收摘要的信箱

### 步驟 3：設定 Gmail 應用程式密碼

1. 前往 [Google 帳戶](https://myaccount.google.com/)
2. 左側選單 → **安全性**
3. 若尚未啟用「兩步驟驗證」，先啟用它
4. 回到安全性頁面 → **應用程式密碼**
5. 選擇「郵件」和「Windows 電腦」(或任意選項)
6. Google 會產生一個 **16 位數字密碼**，複製此密碼作為 `GMAIL_APP_PASSWORD`

### 步驟 4：跳過 Email 寄送（可選）

若不想使用 Email 功能：
- 不設定 `GMAIL_USER` 和 `GMAIL_APP_PASSWORD` 即可
- GitHub Actions 會自動跳過 Email 步驟（印出警告但不中斷）

---

## 🚀 使用方式

### 自動執行

每天 **UTC 00:00**（台灣時間 08:00），自動：
1. 抓取 NewsAPI 新聞
2. 抓取三個電子報
3. 翻譯成繁體中文
4. 發布到網站
5. **寄送 Email 摘要**（若已配置 Gmail）

### 手動執行

在 GitHub 上：
1. 進入 **Actions** 標籤
2. 選擇 **每日新聞自動發布**
3. 點擊 **Run workflow**
4. 完成後會自動寄送 Email

### 本地測試

```bash
# 進入虛擬環境
source venv/bin/activate

# 測試電子報抓取
python3 -c "
import asyncio
from tools.newsletter_fetcher import fetch_newsletters
async def test():
    articles = await fetch_newsletters('tldr', 2)
    print(articles)
asyncio.run(test())
"

# 測試 Email 生成（需設置 .env）
export $(cat .env | xargs)
python agent/send_email.py
```

---

## 📊 Email 格式

發送的 Email 包含：

```
📰 Bit Daily - {日期} 每日新聞摘要

[文章列表]
1. 標題
   摘要內容...
   🔗 查看原文

2. 標題
   摘要內容...
   🔗 查看原文

...

由 Claude News Agent 自動生成
```

HTML 格式，支援各種郵件客戶端。

---

## ⚠️ 已知限制

### The Rundown AI 無法直接爬取

**原因**：該網站使用 Vite + JavaScript SPA，內容在客户端渲染，BeautifulSoup 無法獲取。

**解決方案**：
- 目前會優雅降級（打印警告，不中斷流程）
- 若需要 AI 專項新聞，可透過 NewsAPI 的 technology 分類補充
- 未來可考慮整合 Playwright/Selenium（但會增加依賴和成本）

### 電子報內容變化

TLDR Newsletter、1440 Daily Digest 的頁面結構可能會改變，爬蟲需定期維護。

---

## 🧪 測試清單

升級完成後，建議驗證：

- [ ] 本地：`python agent/main.py` 能否正常抓取新聞並發布
- [ ] 本地：`python agent/send_email.py` 能否生成 Email HTML
- [ ] GitHub Actions：手動執行 workflow，驗證電子報抓取成功
- [ ] GitHub Actions：確認 Email 已寄送到收件箱（可能在垃圾信件夾）

---

## 📞 故障排除

### Email 未寄出

**檢查清單**：
1. ✅ 三個 Secrets（`GMAIL_USER`、`GMAIL_APP_PASSWORD`、`RECIPIENT_EMAIL`）都已設定
2. ✅ `GMAIL_APP_PASSWORD` 是 16 位數字，不是 Google 帳戶密碼
3. ✅ Gmail 帳戶已啟用「兩步驟驗證」
4. ✅ GitHub Actions 日誌中是否有錯誤資訊

**常見錯誤**：
- `SMTPAuthenticationError` → 密碼錯誤或帳號名稱錯誤
- `SMTPException` → Gmail 帳戶可能被鎖定，檢查 Google 安全警告

### 電子報抓取失敗

**TLDR / 1440 失敗**：
- 可能是網頁結構改變，需更新 CSS 選擇器
- 檢查網站是否仍可訪問

**The Rundown AI 失敗**：
- 預期行為（JS 渲染），可安全忽略

### Workflow 日誌查看

在 GitHub Actions 中，可查看詳細日誌：
1. 進入 **Actions** 標籤
2. 選擇最近的 workflow run
3. 點擊 **publish-news** job
4. 檢查各步驟的輸出

---

## 🎉 升級完成！

現在你的 Bit Daily 已支持：
- ✅ 多來源新聞抓取（NewsAPI + 3 個電子報）
- ✅ 每日自動 Email 摘要寄送
- ✅ 繁體中文翻譯
- ✅ 靜態網站發布
- ✅ 完全自動化流程

祝使用愉快！🚀

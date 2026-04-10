# 📰 Bit Daily

一個由 **Claude Agent SDK** 驅動的個人新聞網站，每天自動抓取國際與科技新聞、翻譯成繁體中文，並發布到公開網站。

🌐 **Live Site:** https://claude-news-agent.netlify.app/

---

## ✨ 功能特色

- 🤖 **AI 驅動** — 使用 Claude Agent SDK 自動完成整個新聞處理流程
- 🌍 **多來源抓取** — NewsAPI + 三個電子報（TLDR Newsletter、1440 Daily Digest、The Rundown AI）
- 🈯 **英翻中** — 自動將英文新聞翻譯為繁體中文
- ✉️ **每日 Email 摘要** — GitHub Actions 執行後自動寄送當日新聞摘要（可選）
- 🔗 **手動 URL 模式** — 貼入任意文章網址，Agent 自動讀取、翻譯、發布
- 📝 **靜態網站** — 文章以 Markdown 格式儲存，Hugo 建置為靜態網頁
- 🚀 **全自動部署** — GitHub Actions + Netlify，零手動操作

---

## 🏗️ 系統架構

```
每天 08:00 台灣時間
        │
        ▼
GitHub Actions 觸發
        │
        ▼
Claude Agent SDK
  ├── fetch_news       → 呼叫 NewsAPI 抓取新聞
  ├── fetch_newsletter → 抓取電子報（TLDR、1440、The Rundown AI）
  ├── web_fetch        → 使用原生工具讀取 URL 內容（享受免費 code execution）
  ├── [Agent 內部翻譯] → 分析文章，若為英文自動翻譯成繁體中文
  └── publish          → 輸出 Markdown 文章
        │
        ▼
output/posts/*.md
        │
        ├── 複製到 site/content/posts/
        │
        ▼
Git commit & push
        │
        ▼
Netlify 自動重新建置
        │
        ▼
🌐 網站更新完成
```

---

## 📁 專案結構

```
claude-news-agent/
├── agent/
│   └── main.py                  # Agent 主程式，定義工具與執行邏輯
├── tools/
│   ├── __init__.py
│   ├── news_fetcher.py          # 呼叫 NewsAPI 取得新聞列表
│   ├── newsletter_fetcher.py    # 爬取電子報（TLDR、1440、The Rundown AI）
│   └── publisher.py             # 輸出 Hugo 相容的 Markdown 檔案
├── site/                        # Hugo 靜態網站
│   ├── content/posts/           # 發布的新聞文章
│   ├── themes/ananke/           # Hugo 主題（git submodule）
│   ├── hugo.toml                # Hugo 設定檔
│   └── netlify.toml             # Netlify 部署設定
├── output/
│   └── posts/                   # Agent 輸出的原始 Markdown
├── .github/
│   └── workflows/
│       └── daily-news.yml       # GitHub Actions 排程設定
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## 🔧 環境需求

### 系統需求

| 工具 | 版本 | 安裝方式 |
|------|------|----------|
| Python | 3.11+ | `sudo apt install python3` |
| Node.js | 20+ | `curl -fsSL https://deb.nodesource.com/setup_20.x \| sudo -E bash - && sudo apt install nodejs` |
| Hugo | 0.147.0+ | 見下方說明 |
| Git | 任意版本 | `sudo apt install git` |

### 安裝 Hugo 0.147.0（Ubuntu）

```bash
wget https://github.com/gohugoio/hugo/releases/download/v0.147.0/hugo_extended_0.147.0_linux-amd64.deb
sudo dpkg -i hugo_extended_0.147.0_linux-amd64.deb
hugo version
```

### Python 套件

```
anthropic>=0.40.0        # Anthropic Python SDK
claude-agent-sdk>=0.1.0  # Claude Agent SDK
python-dotenv>=1.0.0     # 載入 .env 環境變數
```

### API Keys

| 服務 | 用途 | 免費方案 | 申請連結 |
|------|------|----------|----------|
| Anthropic | Claude Agent + 翻譯 | 需儲值，最低 $5 美元 | https://console.anthropic.com/ |
| NewsAPI | 抓取每日新聞 | 每天 100 次請求 | https://newsapi.org/register |
| Gmail SMTP | 每日 Email 摘要寄送（選項） | 需要 Gmail 帳號 | https://myaccount.google.com/ |

**電子報來源**（無需 API Key，自動爬取）：
- TLDR Newsletter (https://tldr.tech) — 科技 + AI 新聞
- 1440 Daily Digest (https://join1440.com) — 國際綜合
- The Rundown AI (https://therundown.ai) — AI 專項

---

## 🚀 本地安裝步驟

### 1. Clone 專案

```bash
git clone git@github.com:imissmyselfer/claude-news-agent.git
cd claude-news-agent
```

### 2. 建立虛擬環境並安裝套件

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 設定環境變數

```bash
cp .env.example .env
nano .env
```

填入你的 API Keys：

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxx
NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

載入環境變數：

```bash
export $(cat .env | xargs)
```

### 4. 執行 Agent

**每日自動模式**（抓取當日新聞）：
```bash
python agent/main.py
```

**手動 URL 模式**（指定文章網址）：
```bash
python agent/main.py --url https://techcrunch.com/some-article
```

### 5. 預覽網站

```bash
cd site
hugo server --buildDrafts
# 開啟 http://localhost:1313/
```

---

## ⚙️ GitHub Actions 自動排程

### 設定 Secrets

前往 GitHub Repo → **Settings** → **Secrets and variables** → **Actions** → 新增：

| Secret 名稱 | 值 |
|-------------|-----|
| `ANTHROPIC_API_KEY` | 你的 Anthropic API Key |
| `NEWS_API_KEY` | 你的 NewsAPI Key |
| `GMAIL_USER` | 你的 Gmail 信箱（用於寄送每日摘要） |
| `GMAIL_APP_PASSWORD` | Gmail 應用程式專用密碼（16 位數字密碼） |
| `RECIPIENT_EMAIL` | 接收每日摘要的信箱 |

### 設定 Workflow 權限

前往 **Settings** → **Actions** → **General** → **Workflow permissions** → 選擇 **Read and write permissions** → **Save**

### 排程時間

- 自動執行：每天 **UTC 00:00**（台灣時間早上 **08:00**）
- 手動執行：GitHub → Actions → 每日新聞自動發布 → **Run workflow**
- 手動 URL 模式：Run workflow 時在 URL 欄位填入文章網址

### ✉️ 配置每日 Email 摘要（選項）

若要啟用每日 Email 寄送功能，需要設定 Gmail：

**步驟 1：啟用 Gmail 應用程式密碼**

1. 前往 [Google 帳戶](https://myaccount.google.com/)
2. 左側選單 → **安全性**
3. 啟用「兩步驟驗證」（若尚未啟用）
4. 回到安全性頁面 → **應用程式密碼**
5. 選擇「郵件」和「Windows 電腦」(或任意選項)
6. Google 會產生一個 **16 位數字密碼**，複製此密碼

**步驟 2：設定 GitHub Secrets**

新增以下三個 Secrets：
- `GMAIL_USER`: 你的 Gmail 信箱 (如 `your-email@gmail.com`)
- `GMAIL_APP_PASSWORD`: 上面複製的 16 位數字密碼
- `RECIPIENT_EMAIL`: 接收摘要的信箱（可與 GMAIL_USER 相同或不同）

**完成後**，GitHub Actions 執行完畢後會自動寄送當日新聞摘要至指定信箱。

---

## 🌐 Netlify 部署

1. 前往 https://netlify.com，使用 GitHub 帳號登入
2. **Add new site** → **Import an existing project** → 選擇 `claude-news-agent`
3. 填入建置設定：
   - Base directory: `site`
   - Build command: `hugo`
   - Publish directory: `site/public`
4. 點擊 **Deploy site**

每次 GitHub Actions 推送新文章，Netlify 會自動重新建置網站。

---

## 🔄 完整自動化流程

```
每天 08:00 台灣時間
    │
    ├─ GitHub Actions 啟動
    ├─ 安裝 Python 套件 + Claude CLI
    ├─ 執行 python agent/main.py（單一 Agent API 呼叫）
    │     ├─ fetch_news (國際新聞 x3)
    │     ├─ fetch_news (科技新聞 x3)
    │     ├─ fetch_news (本地新聞 x3)
    │     ├─ fetch_newsletter (TLDR 新聞 x3)
    │     ├─ fetch_newsletter (1440 新聞 x3)
    │     ├─ fetch_newsletter (The Rundown AI x3)
    │     ├─ web_fetch (讀取每篇文章 URL)
    │     ├─ [Agent 內部翻譯] (分析內容 + 自動翻譯)
    │     └─ publish (輸出 Markdown)
    ├─ 複製文章到 site/content/posts/
    ├─ git commit & push
    ├─ Netlify 自動重新建置 → 網站更新 ✅
    └─ 寄送每日摘要 Email（若已配置 Gmail）→ Email 發送 ✅
```

---

## 🚀 架構優化（v2.0+）

本專案經過優化，採用最高效的 Claude Agent SDK 使用模式：

| 優化項目 | 改動 | 收益 |
|---------|------|------|
| **Web 內容讀取** | 改用 Claude 原生 `web_fetch` 工具 | ✓ 享受免費 code execution<br>✓ 移除 BeautifulSoup 依賴 |
| **翻譯整合** | 改由 Agent 內部進行文章翻譯 | ✓ 單一 API 呼叫<br>✓ Context 完全共享<br>✓ 減少 token 消耗 |
| **Prompt Caching** | 待 Agent SDK v0.2.0+ 支持 | ✓ 每日重複 prompt 費用降 90% |

**結果**：整個新聞抓取→翻譯→發布流程在一次 Agent API 呼叫中完成，最大化效率與成本控制。

---

## 📄 授權

MIT License

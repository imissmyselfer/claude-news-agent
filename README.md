# 📰 個人新聞台 — Personal News Agent

一個由 **Claude Agent SDK** 驅動的個人新聞網站，每天自動抓取國際與科技新聞、翻譯成繁體中文，並發布到公開網站。

🌐 **Live Site:** https://claude-news-agent.netlify.app/

---

## ✨ 功能特色

- 🤖 **AI 驅動** — 使用 Claude Agent SDK 自動完成整個新聞處理流程
- 🌍 **每日自動抓取** — 每天早上 8:00（台灣時間）自動執行
- 🈯 **英翻中** — 自動將英文新聞翻譯為繁體中文
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
  ├── fetch_news   → 呼叫 NewsAPI 抓取新聞
  ├── read_url     → 讀取指定 URL 文章內容
  ├── translate    → 英文翻譯繁體中文
  └── publish      → 輸出 Markdown 文章
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
│   ├── url_reader.py            # 抓取並解析任意網頁內容
│   ├── translator.py            # 英翻中（呼叫 Claude Messages API）
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
aiohttp>=3.9.0           # 非同步 HTTP 請求
beautifulsoup4>=4.12.0   # HTML 解析（URL 讀取工具）
python-dotenv>=1.0.0     # 載入 .env 環境變數
```

### API Keys

| 服務 | 用途 | 免費方案 | 申請連結 |
|------|------|----------|----------|
| Anthropic | Claude Agent + 翻譯 | 需儲值，最低 $5 美元 | https://console.anthropic.com/ |
| NewsAPI | 抓取每日新聞 | 每天 100 次請求 | https://newsapi.org/register |

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

### 設定 Workflow 權限

前往 **Settings** → **Actions** → **General** → **Workflow permissions** → 選擇 **Read and write permissions** → **Save**

### 排程時間

- 自動執行：每天 **UTC 00:00**（台灣時間早上 **08:00**）
- 手動執行：GitHub → Actions → 每日新聞自動發布 → **Run workflow**
- 手動 URL 模式：Run workflow 時在 URL 欄位填入文章網址

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
    ├─ 執行 python agent/main.py
    │     ├─ fetch_news (國際新聞 x3)
    │     ├─ fetch_news (科技新聞 x3)
    │     ├─ translate (翻譯每篇文章)
    │     └─ publish (輸出 Markdown)
    ├─ 複製文章到 site/content/posts/
    ├─ git commit & push
    └─ Netlify 自動重新建置 → 網站更新 ✅
```

---

## 🛠️ Agent SDK vs Messages API

本專案混合使用兩種 Anthropic API：

| | 使用場景 | 原因 |
|--|----------|------|
| **Claude Agent SDK** | 主要工作流程 | 需要工具迴圈（抓取→翻譯→發布） |
| **Messages API** | 翻譯工具內部 | 翻譯是單一明確任務，不需要 Agent 迴圈，更省 token |

---

## 📄 授權

MIT License

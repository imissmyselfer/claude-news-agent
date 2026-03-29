# 📰 個人新聞台 Agent

使用 Claude Agent SDK 自動抓取、翻譯、發布每日新聞的個人新聞站。

## 功能

- 每天早上自動抓取國際與科技新聞（透過 GitHub Actions）
- 英文文章自動翻譯為繁體中文
- 支援手動貼入 URL，讓 Agent 讀取並編輯發布
- 文章以 Markdown 格式輸出，相容 Hugo / Eleventy / Jekyll

## 專案結構

```
personal-news-agent/
├── agent/
│   └── main.py              # Agent 主程式（工具定義 + 執行邏輯）
├── tools/
│   ├── news_fetcher.py      # 呼叫 NewsAPI 取得新聞
│   ├── url_reader.py        # 抓取指定 URL 的文章內容
│   ├── translator.py        # 英翻中（呼叫 Claude Messages API）
│   └── publisher.py         # 輸出 Markdown 檔案
├── output/
│   └── posts/               # 自動產生的新聞文章（Markdown）
├── .github/
│   └── workflows/
│       └── daily-news.yml   # GitHub Actions 排程設定
├── requirements.txt
└── .env.example
```

## 快速開始

### 1. 取得 API Keys

| 服務 | 用途 | 免費方案 |
|---|---|---|
| [Anthropic](https://console.anthropic.com/) | Claude Agent + 翻譯 | 有免費額度 |
| [NewsAPI](https://newsapi.org/register) | 抓取新聞 | 每月 1,000 次 |

### 2. 本地設定

```bash
# 複製專案
git clone https://github.com/你的帳號/personal-news-agent
cd personal-news-agent

# 安裝 Claude CLI（Agent SDK 需要）
curl -fsSL https://claude.ai/install.sh | sh

# 安裝 Python 套件
pip install -r requirements.txt

# 建立環境變數檔案
cp .env.example .env
# 編輯 .env，填入你的 API Keys
```

### 3. 設定 .env

```env
ANTHROPIC_API_KEY=sk-ant-xxxxxx
NEWS_API_KEY=xxxxxxxxxxxxxxxx
```

### 4. 本地測試

```bash
# 自動模式（抓當日新聞）
python agent/main.py

# 手動 URL 模式
python agent/main.py --url https://techcrunch.com/2025/01/01/some-article
```

## 設定 GitHub Actions 自動排程

1. 到 GitHub Repo → **Settings** → **Secrets and variables** → **Actions**
2. 新增兩個 Repository secrets：
   - `ANTHROPIC_API_KEY`
   - `NEWS_API_KEY`
3. 每天 UTC 00:00（台灣時間早上 8:00）自動執行
4. 也可在 **Actions** 分頁手動觸發，並可貼入 URL

## 連接靜態網站

文章產生在 `output/posts/` 資料夾，格式相容主流靜態框架：

**Hugo（推薦）**
```bash
hugo new site my-news-site
# 把 output/posts/ 對應到 content/posts/
```

**Netlify 自動部署**
- 連接 GitHub Repo 到 Netlify
- Build command: `hugo`
- Publish directory: `public`
- 每次 Agent 推送新文章，Netlify 自動重新建置

## 手動觸發（貼入 URL）

到 GitHub → Actions → 每日新聞自動發布 → Run workflow → 填入 URL

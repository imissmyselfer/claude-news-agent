#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 檢查今天是否已經跑過
LOCKFILE="/tmp/claude-news-$(date '+%Y-%m-%d').lock"
if [ -f "$LOCKFILE" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - 今天已經跑過，跳過。"
    exit 0
fi
touch "$LOCKFILE"

cd /home/erin/Working/claude/claude-news-agent
echo "========================================"
echo "🕐 Started at: $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

set -a
source .env
set +a
unset ANTHROPIC_API_KEY
unset ANTHROPIC_BASE_URL
unset ANTHROPIC_AUTH_TOKEN

CLAUDE_BIN="/home/erin/.local/bin/claude"

# ── 信 1：國際 + 科技新聞 ──
echo ""
echo "📰 信 1：國際與科技新聞"
echo "----"
$CLAUDE_BIN --dangerously-skip-permissions -p "搜尋今日最重要的國際新聞5則和科技新聞5則，來源必須是英文主流媒體（BBC、Reuters、TechCrunch、The Verge 等）。直接輸出純 HTML，不要用 markdown code block 包裝，不要有任何前言或說明文字，只輸出 HTML 內容。每則新聞必須包含：分類標籤（國際/科技）、標題、來源名稱、原始文章 URL、2-3 句繁體中文摘要。" | python3 agent/send_email.py --label "國際與科技新聞"

# ── 信 2：南灣當地新聞 ──
echo ""
echo "📰 信 2：南灣當地新聞"
echo "----"
$CLAUDE_BIN --dangerously-skip-permissions -p "搜尋今日最重要的矽谷南灣地區新聞8則，重點包括 Los Altos、Mountain View、Palo Alto、Sunnyvale、Santa Clara、San Jose 等地。來源包括 Palo Alto Online、Mercury News、SF Chronicle 等。直接輸出純 HTML，不要用 markdown code block 包裝，每則新聞必須包含：地區、標題、來源名稱、原始文章 URL、2-3 句繁體中文摘要。" | python3 agent/send_email.py --label "南灣當地新聞"

echo ""
echo "✅ Finished at: $(date '+%Y-%m-%d %H:%M:%S')"

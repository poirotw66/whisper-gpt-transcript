#!/bin/bash

# 啟動後端服務
cd backend

# 檢查環境變數
if [ -z "$OPENAI_API_KEY" ]; then
    echo "錯誤: 請設定 OPENAI_API_KEY 環境變數"
    echo "使用: export OPENAI_API_KEY='your-api-key'"
    exit 1
fi

# 檢查 FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "錯誤: FFmpeg 未安裝"
    echo "macOS: brew install ffmpeg"
    echo "Ubuntu/Debian: sudo apt-get install ffmpeg"
    exit 1
fi

# 啟動服務
echo "啟動後端服務於 http://localhost:8000"
python main.py


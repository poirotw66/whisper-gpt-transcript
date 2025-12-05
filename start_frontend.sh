#!/bin/bash

# 啟動前端服務
cd frontend

# 檢查 Node.js
if ! command -v node &> /dev/null; then
    echo "錯誤: Node.js 未安裝"
    exit 1
fi

# 檢查是否已安裝依賴
if [ ! -d "node_modules" ]; then
    echo "安裝前端依賴..."
    npm install
fi

# 啟動開發伺服器
echo "啟動前端服務於 http://localhost:5173"
npm run dev


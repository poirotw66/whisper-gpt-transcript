# 影片即時字幕生成器

一個基於 OpenAI Realtime API 的影片即時字幕生成 Web 應用，支援影片上傳、即時轉錄、繁體中文翻譯、SRT 匯出和自動筆記生成。

## 功能特點

- ✅ 影片上傳與播放
- ✅ 即時語音轉文字（使用 OpenAI Realtime API）
- ✅ 繁體中文翻譯
- ✅ SRT 字幕檔匯出
- ✅ 自動生成影片筆記（摘要、重點、關鍵詞）

## 技術架構

### 後端
- FastAPI - Python Web 框架
- WebSocket - 即時通訊
- FFmpeg - 音訊提取
- OpenAI Realtime API - 語音轉文字
- OpenAI GPT-4o - 筆記生成與翻譯

### 前端
- React 18 + TypeScript
- Vite - 建置工具
- Tailwind CSS - 樣式框架
- WebSocket - 即時字幕接收

## 安裝與設定

### 前置需求

1. Python 3.8+
2. Node.js 18+
3. FFmpeg（需安裝在系統 PATH 中）

#### macOS 安裝 FFmpeg
```bash
brew install ffmpeg
```

#### Ubuntu/Debian 安裝 FFmpeg
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### 後端設定

1. 進入後端目錄：
```bash
cd backend
```

2. 安裝 Python 依賴：
```bash
pip install -r requirements.txt
```

3. 設定環境變數：
```bash
export OPENAI_API_KEY='your-api-key-here'
```

4. 啟動後端服務：
```bash
python main.py
```

後端將在 `http://localhost:8000` 運行

### 前端設定

1. 進入前端目錄：
```bash
cd frontend
```

2. 安裝依賴：
```bash
npm install
```

3. 啟動開發伺服器：
```bash
npm run dev
```

前端將在 `http://localhost:5173` 運行

## 使用說明

1. **上傳影片**：點擊上傳區域選擇影片檔案（支援 MP4, MOV, AVI 等格式，最大 500MB）

2. **開始轉錄**：點擊播放按鈕開始播放影片，系統會自動開始轉錄並即時顯示字幕

3. **選擇語言**：可以切換顯示原文或繁體中文（需要先點擊翻譯）

4. **匯出字幕**：轉錄完成後，可以匯出 SRT 格式的字幕檔

5. **查看筆記**：影片播放完畢後，系統會自動生成結構化筆記，包含摘要、重點和關鍵詞

## API 端點

### 後端 API

- `POST /upload` - 上傳影片
- `GET /video/{video_id}` - 取得影片檔案
- `WebSocket /ws/transcribe/{video_id}` - 即時轉錄串流
- `POST /translate/{video_id}` - 翻譯字幕為繁體中文
- `POST /generate-notes/{video_id}` - 生成影片筆記
- `GET /subtitles/{video_id}` - 取得字幕資料
- `GET /export/srt/{video_id}` - 匯出 SRT 字幕檔

## 專案結構

```
Realtimegpt-transcript/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── audio_extractor.py   # 音訊提取模組
│   ├── realtime_client.py   # Realtime API 客戶端
│   ├── translator.py        # 翻譯服務
│   ├── note_generator.py    # 筆記生成服務
│   └── requirements.txt     # Python 依賴
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/      # React 元件
│   │   ├── hooks/           # 自訂 Hooks
│   │   └── utils/           # 工具函數
│   └── package.json
├── uploads/                 # 上傳檔案暫存
└── audio_cache/            # 音訊快取
```

## 注意事項

- 需要有效的 OpenAI API Key，且需支援 Realtime API 和 GPT-4o
- 影片檔案會暫存在 `uploads/` 目錄
- 音訊檔案會暫存在 `audio_cache/` 目錄
- 建議定期清理暫存檔案

## 授權

MIT License


# 影片即時字幕生成器

一個基於 OpenAI Whisper API 的影片字幕生成 Web 應用，支援影片上傳、精確時間戳轉錄、繁體中文翻譯、SRT 匯出和雙語筆記生成。

## 功能特點

- ✅ 影片上傳與播放
- ✅ 語音轉文字（使用 OpenAI Whisper API，精確時間戳）
- ✅ 即時字幕顯示（影片播放時同步顯示）
- ✅ 繁體中文翻譯（字幕逐條翻譯）
- ✅ SRT 字幕檔匯出（支援原文/繁體中文）
- ✅ 雙語筆記生成（原文版本 + 繁體中文版本）

## 技術架構

### 後端
- **FastAPI** - Python Web 框架
- **WebSocket** - 即時通訊
- **FFmpeg** - 音訊提取（24kHz PCM WAV）
- **OpenAI Whisper API** - 語音轉文字（精確時間戳）
- **OpenAI GPT-4o-mini** - 筆記生成與翻譯

### 前端
- **React 18 + TypeScript** - 前端框架
- **Vite** - 建置工具
- **Tailwind CSS** - 樣式框架
- **WebSocket** - 即時字幕接收

## 系統流程

```
┌─────────────────────────────────────────────────────────────────┐
│                         系統流程圖                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. 上傳影片                                                     │
│     └─→ POST /upload                                            │
│         └─→ FFmpeg 提取音訊 (24kHz WAV)                         │
│                                                                  │
│  2. 開始轉錄                                                     │
│     └─→ WebSocket /ws/transcribe/{video_id}                     │
│         └─→ Whisper API 轉錄 (精確時間戳)                       │
│         └─→ 即時推送字幕到前端                                   │
│                                                                  │
│  3. 生成筆記                                                     │
│     └─→ POST /generate-notes/{video_id}                         │
│         └─→ GPT-4o-mini 生成雙語筆記                            │
│                                                                  │
│  4. 翻譯字幕 (可選)                                              │
│     └─→ POST /translate/{video_id}                              │
│         └─→ GPT-4o-mini 逐條翻譯                                │
│                                                                  │
│  5. 匯出 SRT                                                     │
│     └─→ GET /export/srt/{video_id}                              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 安裝與設定

### 前置需求

1. Python 3.8+
2. Node.js 18+
3. FFmpeg（需安裝在系統 PATH 中）
4. OpenAI API Key

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
# 或使用啟動腳本
./start_backend.sh
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
# 或使用啟動腳本
./start_frontend.sh
```

前端將在 `http://localhost:5173` 運行

## 使用說明

1. **上傳影片**：點擊上傳區域選擇影片檔案（支援 MP4, MOV, AVI 等格式，最大 500MB）

2. **開始轉錄**：點擊播放按鈕開始播放影片，系統會自動開始轉錄

3. **查看字幕**：
   - 即時字幕會顯示在影片下方
   - 完整字幕列表顯示在字幕區域

4. **切換語言**：
   - 選擇「原文」顯示原始語言字幕
   - 選擇「繁體中文」觸發翻譯（首次需要等待翻譯完成）

5. **匯出字幕**：點擊匯出按鈕下載 SRT 格式字幕檔

6. **查看筆記**：
   - 轉錄完成後自動生成雙語筆記
   - 可切換原文/繁體中文版本
   - 包含：摘要、重點整理、關鍵詞、深入見解

## API 端點

### 後端 API

| 端點 | 方法 | 說明 |
|------|------|------|
| `/upload` | POST | 上傳影片 |
| `/video/{video_id}` | GET | 取得影片檔案 |
| `/ws/transcribe/{video_id}` | WebSocket | 即時轉錄串流 |
| `/translate/{video_id}` | POST | 翻譯字幕為繁體中文 |
| `/generate-notes/{video_id}` | POST | 生成雙語筆記 |
| `/subtitles/{video_id}` | GET | 取得字幕資料 |
| `/export/srt/{video_id}` | GET | 匯出 SRT 字幕檔 |

## 專案結構

```
Realtimegpt-transcript/
├── backend/
│   ├── main.py              # FastAPI 主程式
│   ├── audio_extractor.py   # 音訊提取模組 (FFmpeg)
│   ├── whisper_client.py    # Whisper API 客戶端
│   ├── translator.py        # 翻譯服務 (GPT-4o-mini)
│   ├── note_generator.py    # 筆記生成服務 (GPT-4o-mini)
│   └── requirements.txt     # Python 依賴
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # 主應用元件
│   │   ├── components/      # React 元件
│   │   │   ├── VideoUploader.tsx
│   │   │   ├── VideoPlayer.tsx
│   │   │   ├── SubtitleDisplay.tsx
│   │   │   ├── LanguageSelector.tsx
│   │   │   ├── ExportButton.tsx
│   │   │   └── NotesPanel.tsx
│   │   ├── hooks/           # 自訂 Hooks
│   │   │   └── useWebSocket.ts
│   │   └── utils/           # 工具函數
│   │       └── srtExporter.ts
│   └── package.json
├── uploads/                 # 上傳檔案暫存
├── audio_cache/             # 音訊快取
├── start_backend.sh         # 後端啟動腳本
└── start_frontend.sh        # 前端啟動腳本
```

## 使用的 OpenAI 模型

| 功能 | 模型 | 說明 |
|------|------|------|
| 語音轉文字 | `whisper-1` | 精確時間戳、多語言支援 |
| 筆記生成 | `gpt-4o-mini` | 輕量快速、雙語輸出 |
| 字幕翻譯 | `gpt-4o-mini` | 逐條翻譯、保持語調 |

## 注意事項

- 需要有效的 OpenAI API Key
- 影片檔案會暫存在 `uploads/` 目錄
- 音訊檔案會暫存在 `audio_cache/` 目錄
- 建議定期清理暫存檔案
- 支援多種影片格式（MP4, MOV, AVI, MKV 等）

## 授權

MIT License

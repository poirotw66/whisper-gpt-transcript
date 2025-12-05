"""
FastAPI 主程式 - 影片即時字幕生成服務
"""
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import uuid
from pathlib import Path
from typing import Dict, Optional
import json

from audio_extractor import extract_audio
from realtime_client import RealtimeTranscriptionClient
from translator import translate_to_traditional_chinese
from note_generator import generate_notes

app = FastAPI(title="Video Subtitle API")

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 建立必要的目錄
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
AUDIO_DIR = Path("audio_cache")
AUDIO_DIR.mkdir(exist_ok=True)

# 儲存影片和轉錄資料
video_storage: Dict[str, dict] = {}


@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """上傳影片並提取音訊"""
    video_id = str(uuid.uuid4())
    video_path = UPLOAD_DIR / f"{video_id}_{file.filename}"
    
    # 儲存影片
    with open(video_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 提取音訊
    audio_path = AUDIO_DIR / f"{video_id}.wav"
    try:
        extract_audio(str(video_path), str(audio_path))
        
        video_storage[video_id] = {
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "filename": file.filename,
            "subtitles": [],
            "translated_subtitles": []
        }
        
        return {
            "video_id": video_id,
            "filename": file.filename,
            "message": "影片上傳成功"
        }
    except Exception as e:
        return {"error": f"音訊提取失敗: {str(e)}"}, 500


@app.get("/video/{video_id}")
async def get_video(video_id: str):
    """取得影片檔案"""
    if video_id not in video_storage:
        return {"error": "影片不存在"}, 404
    
    video_path = video_storage[video_id]["video_path"]
    if not os.path.exists(video_path):
        return {"error": "影片檔案不存在"}, 404
    
    return FileResponse(video_path)


@app.websocket("/ws/transcribe/{video_id}")
async def websocket_transcribe(websocket: WebSocket, video_id: str):
    """WebSocket 端點：即時轉錄"""
    await websocket.accept()
    
    if video_id not in video_storage:
        await websocket.send_json({"error": "影片不存在"})
        await websocket.close()
        return
    
    video_data = video_storage[video_id]
    audio_path = video_data["audio_path"]
    
    if not os.path.exists(audio_path):
        await websocket.send_json({"error": "音訊檔案不存在"})
        await websocket.close()
        return
    
    try:
        # 建立 Realtime API 客戶端
        client = RealtimeTranscriptionClient()
        
        # 開始轉錄
        async for subtitle_data in client.transcribe_audio_file(audio_path):
            # 儲存字幕
            video_data["subtitles"].append(subtitle_data)
            
            # 發送到前端
            await websocket.send_json({
                "type": "subtitle",
                "data": subtitle_data
            })
        
        # 轉錄完成
        await websocket.send_json({
            "type": "completed",
            "message": "轉錄完成"
        })
        
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "error": str(e)
        })


@app.post("/translate/{video_id}")
async def translate_subtitles(video_id: str):
    """翻譯字幕為繁體中文"""
    if video_id not in video_storage:
        return {"error": "影片不存在"}, 404
    
    video_data = video_storage[video_id]
    subtitles = video_data["subtitles"]
    
    if not subtitles:
        return {"error": "尚無字幕可翻譯"}, 400
    
    try:
        translated = []
        for subtitle in subtitles:
            translated_text = await translate_to_traditional_chinese(subtitle["text"])
            translated_subtitle = {
                **subtitle,
                "translated_text": translated_text
            }
            translated.append(translated_subtitle)
        
        video_data["translated_subtitles"] = translated
        
        return {
            "message": "翻譯完成",
            "translated_count": len(translated)
        }
    except Exception as e:
        return {"error": f"翻譯失敗: {str(e)}"}, 500


@app.post("/generate-notes/{video_id}")
async def generate_video_notes(video_id: str):
    """生成影片筆記"""
    if video_id not in video_storage:
        return {"error": "影片不存在"}, 404
    
    video_data = video_storage[video_id]
    subtitles = video_data["subtitles"]
    
    if not subtitles:
        return {"error": "尚無字幕可生成筆記"}, 400
    
    # 組合所有字幕文字
    full_text = " ".join([s["text"] for s in subtitles])
    
    try:
        notes = await generate_notes(full_text)
        return {
            "notes": notes,
            "message": "筆記生成完成"
        }
    except Exception as e:
        return {"error": f"筆記生成失敗: {str(e)}"}, 500


@app.get("/subtitles/{video_id}")
async def get_subtitles(video_id: str, language: Optional[str] = "original"):
    """取得字幕資料"""
    if video_id not in video_storage:
        return {"error": "影片不存在"}, 404
    
    video_data = video_storage[video_id]
    
    if language == "traditional":
        subtitles = video_data.get("translated_subtitles", [])
    else:
        subtitles = video_data["subtitles"]
    
    return {"subtitles": subtitles}


@app.get("/export/srt/{video_id}")
async def export_srt(video_id: str, language: Optional[str] = "original"):
    """匯出 SRT 字幕檔"""
    if video_id not in video_storage:
        return {"error": "影片不存在"}, 404
    
    video_data = video_storage[video_id]
    
    if language == "traditional":
        subtitles = video_data.get("translated_subtitles", [])
        text_key = "translated_text"
    else:
        subtitles = video_data["subtitles"]
        text_key = "text"
    
    if not subtitles:
        return {"error": "尚無字幕可匯出"}, 400
    
    # 生成 SRT 內容
    srt_content = ""
    for idx, subtitle in enumerate(subtitles, 1):
        start_time = format_timestamp(subtitle["start_time"])
        end_time = format_timestamp(subtitle["end_time"])
        text = subtitle.get(text_key, subtitle["text"])
        
        srt_content += f"{idx}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
    
    # 儲存 SRT 檔案
    srt_path = UPLOAD_DIR / f"{video_id}_{language}.srt"
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)
    
    return FileResponse(
        srt_path,
        media_type="text/plain",
        filename=f"{video_data['filename']}_{language}.srt"
    )


def format_timestamp(seconds: float) -> str:
    """將秒數轉換為 SRT 時間格式 (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


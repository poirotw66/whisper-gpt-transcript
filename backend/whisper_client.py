"""
Whisper API 客戶端 - 處理音訊轉錄（精確時間戳）
"""
import os
from openai import OpenAI
from typing import List, Dict, Any


class WhisperTranscriptionClient:
    """OpenAI Whisper API 轉錄客戶端"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 環境變數未設定")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe_audio_file(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        使用 Whisper API 轉錄音訊檔案，獲取精確時間戳
        
        Args:
            audio_path: 音訊檔案路徑
            
        Returns:
            字幕列表，每個字幕包含 {id, start_time, end_time, text}
        """
        print(f"開始使用 Whisper API 轉錄: {audio_path}")
        
        try:
            with open(audio_path, "rb") as audio_file:
                print(f"音訊檔案大小: {os.path.getsize(audio_path)} bytes")
                
                # 使用 verbose_json 格式獲取詳細時間戳
                print("正在調用 Whisper API...")
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="verbose_json",
                    timestamp_granularities=["segment"]  # 獲取段落級時間戳
                )
                print(f"Whisper API 返回成功")
            
            subtitles = []
            
            # 調試：打印原始響應結構
            print(f"響應類型: {type(response)}")
            print(f"響應屬性: {dir(response)}")
            
            # 處理轉錄結果
            if hasattr(response, 'segments') and response.segments:
                print(f"找到 {len(response.segments)} 個段落")
                for idx, segment in enumerate(response.segments, 1):
                    # segment 可能是對象或字典
                    if hasattr(segment, 'start'):
                        start_time = segment.start
                        end_time = segment.end
                        text = segment.text
                    else:
                        start_time = segment.get("start", 0.0)
                        end_time = segment.get("end", 0.0)
                        text = segment.get("text", "")
                    
                    subtitle = {
                        "id": idx,
                        "start_time": float(start_time),
                        "end_time": float(end_time),
                        "text": text.strip() if text else ""
                    }
                    
                    if subtitle["text"]:  # 只添加有內容的字幕
                        subtitles.append(subtitle)
                        print(f"字幕 {idx}: {subtitle['start_time']:.2f}s - {subtitle['end_time']:.2f}s: {subtitle['text'][:30]}...")
            else:
                print(f"警告：沒有找到 segments 屬性")
                # 嘗試獲取純文字
                if hasattr(response, 'text') and response.text:
                    print(f"找到純文字: {response.text[:100]}...")
                    subtitles.append({
                        "id": 1,
                        "start_time": 0.0,
                        "end_time": 60.0,  # 預設 60 秒
                        "text": response.text.strip()
                    })
            
            print(f"轉錄完成，共 {len(subtitles)} 段字幕")
            return subtitles
            
        except Exception as e:
            print(f"Whisper API 錯誤: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def transcribe_with_word_timestamps(self, audio_path: str, max_segment_duration: float = 2.0) -> List[Dict[str, Any]]:
        """
        使用 Whisper API 轉錄音訊檔案，獲取字詞級時間戳並按時間分段
        
        Args:
            audio_path: 音訊檔案路徑
            max_segment_duration: 每段字幕最大時長（秒）
            
        Returns:
            字幕列表，每個字幕包含 {id, start_time, end_time, text}
        """
        print(f"開始使用 Whisper API 轉錄（字詞級時間戳）: {audio_path}")
        
        with open(audio_path, "rb") as audio_file:
            # 獲取字詞和段落級時間戳
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word", "segment"]
            )
        
        subtitles = []
        subtitle_id = 0
        
        # 如果有字詞級時間戳，按時間分段
        if hasattr(response, 'words') and response.words:
            current_segment = {
                "start_time": None,
                "end_time": None,
                "words": []
            }
            
            for word_info in response.words:
                word = word_info.get("word", "")
                start = word_info.get("start", 0.0)
                end = word_info.get("end", 0.0)
                
                # 初始化段落開始時間
                if current_segment["start_time"] is None:
                    current_segment["start_time"] = start
                
                # 檢查是否需要分段（超過最大時長或遇到標點符號）
                should_split = False
                if current_segment["start_time"] is not None:
                    duration = end - current_segment["start_time"]
                    if duration >= max_segment_duration:
                        should_split = True
                
                # 遇到句號、問號、驚嘆號等標點也分段
                if word.rstrip() and word.rstrip()[-1] in '。！？.!?':
                    should_split = True
                
                current_segment["words"].append(word)
                current_segment["end_time"] = end
                
                if should_split and current_segment["words"]:
                    subtitle_id += 1
                    text = "".join(current_segment["words"]).strip()
                    
                    if text:
                        subtitles.append({
                            "id": subtitle_id,
                            "start_time": current_segment["start_time"],
                            "end_time": current_segment["end_time"],
                            "text": text
                        })
                        print(f"字幕 {subtitle_id}: {current_segment['start_time']:.2f}s - {current_segment['end_time']:.2f}s: {text[:30]}...")
                    
                    # 重置段落
                    current_segment = {
                        "start_time": None,
                        "end_time": None,
                        "words": []
                    }
            
            # 處理最後一段
            if current_segment["words"]:
                subtitle_id += 1
                text = "".join(current_segment["words"]).strip()
                
                if text:
                    subtitles.append({
                        "id": subtitle_id,
                        "start_time": current_segment["start_time"],
                        "end_time": current_segment["end_time"],
                        "text": text
                    })
        
        # 如果沒有字詞級時間戳，使用段落級
        elif hasattr(response, 'segments') and response.segments:
            for idx, segment in enumerate(response.segments, 1):
                subtitle = {
                    "id": idx,
                    "start_time": segment.get("start", 0.0),
                    "end_time": segment.get("end", 0.0),
                    "text": segment.get("text", "").strip()
                }
                
                if subtitle["text"]:
                    subtitles.append(subtitle)
        
        print(f"轉錄完成，共 {len(subtitles)} 段字幕")
        return subtitles


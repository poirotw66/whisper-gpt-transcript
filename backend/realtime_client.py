"""
OpenAI Realtime API 客戶端 - 處理音訊轉錄
"""
import asyncio
import websockets
import json
import base64
import os
import wave
from typing import AsyncIterator, Dict, Any


class RealtimeTranscriptionClient:
    """OpenAI Realtime API 轉錄客戶端"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 環境變數未設定")
        
        self.realtime_url = "wss://api.openai.com/v1/realtime?model=gpt-realtime-mini-2025-10-06"
        self.sample_rate = 24000
        self.chunk_size = 4096
    
    async def transcribe_audio_file(self, audio_path: str) -> AsyncIterator[Dict[str, Any]]:
        """
        轉錄音訊檔案並產生字幕
        
        Args:
            audio_path: 音訊檔案路徑
            
        Yields:
            字幕資料字典: {start_time, end_time, text}
        """
        # 先獲取音訊檔案資訊
        import wave
        with wave.open(audio_path, 'rb') as wav_file:
            sample_rate = wav_file.getframerate()
            total_frames = wav_file.getnframes()
            audio_duration = total_frames / sample_rate
            print(f"音訊檔案資訊: {audio_duration:.2f} 秒, {total_frames} frames, {sample_rate} Hz")
        
        async with websockets.connect(
            self.realtime_url,
            additional_headers={
                "Authorization": f"Bearer {self.api_key}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as websocket:
            # 配置轉錄會話
            # 對於預錄檔案，使用較寬鬆的 VAD 設定以確保完整轉錄
            session_config = {
                "type": "session.update",
                "session": {
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.3,  # 降低閾值，更容易檢測語音
                        "prefix_padding_ms": 500,  # 增加前綴填充
                        "silence_duration_ms": 1000  # 增加靜音持續時間，避免過早分段
                    }
                }
            }
            await websocket.send(json.dumps(session_config))
            print("轉錄會話已配置")
            
            # 使用 Queue 來收集轉錄結果
            subtitle_queue = asyncio.Queue()
            send_complete = asyncio.Event()
            receive_complete = asyncio.Event()
            error_occurred = asyncio.Event()
            error_message = [None]
            
            # 啟動發送任務
            async def send_wrapper():
                try:
                    await self._send_audio_data(websocket, audio_path)
                    # 發送結束訊號，告訴 API 音訊已全部發送
                    try:
                        await websocket.send(json.dumps({
                            "type": "input_audio_buffer.commit"
                        }))
                        print("已發送所有音訊資料並提交")
                    except websockets.exceptions.ConnectionClosed:
                        print("連接已關閉，無法發送 commit")
                    send_complete.set()
                except Exception as e:
                    error_message[0] = str(e)
                    error_occurred.set()
                    send_complete.set()
            
            # 啟動接收任務
            async def receive_wrapper():
                try:
                    async for subtitle in self._receive_transcriptions(websocket):
                        await subtitle_queue.put(subtitle)
                    receive_complete.set()
                except Exception as e:
                    error_message[0] = str(e)
                    error_occurred.set()
                    receive_complete.set()
            
            send_task = asyncio.create_task(send_wrapper())
            receive_task = asyncio.create_task(receive_wrapper())
            
            # 持續 yield 字幕，直到接收完成
            while True:
                # 檢查是否有錯誤
                if error_occurred.is_set():
                    if error_message[0]:
                        raise Exception(error_message[0])
                    break
                
                # 檢查是否完成（發送完成且接收完成且 queue 為空）
                if send_complete.is_set() and receive_complete.is_set() and subtitle_queue.empty():
                    break
                
                # 嘗試從 queue 取得字幕（設定超時避免阻塞）
                try:
                    subtitle = await asyncio.wait_for(
                        subtitle_queue.get(),
                        timeout=0.5
                    )
                    yield subtitle
                except asyncio.TimeoutError:
                    # 如果 queue 為空，檢查是否應該結束
                    if send_complete.is_set() and receive_complete.is_set():
                        # 再檢查一次 queue 是否真的為空
                        try:
                            subtitle = subtitle_queue.get_nowait()
                            yield subtitle
                        except asyncio.QueueEmpty:
                            break
                    continue
            
            # 等待任務完成（確保清理）
            await asyncio.gather(send_task, receive_task, return_exceptions=True)
    
    async def _send_audio_data(self, websocket, audio_path: str):
        """發送音訊資料到 Realtime API"""
        try:
            with wave.open(audio_path, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                sample_width = wav_file.getsampwidth()
                total_frames = wav_file.getnframes()
                
                # 計算每個 frame 的位元組數
                bytes_per_frame = channels * sample_width
                
                # 計算每個 chunk 應該讀取的 frames 數
                # chunk_size 是位元組數，我們希望每次發送約 20ms 的音訊
                frames_per_chunk = int(sample_rate * 0.02)  # 20ms 的音訊
                bytes_per_chunk = frames_per_chunk * bytes_per_frame
                
                bytes_sent = 0
                chunks_sent = 0
                total_bytes = total_frames * bytes_per_frame
                
                print(f"開始發送音訊: 總共 {total_frames} frames, {total_bytes} 位元組")
                
                # 快速發送所有音訊資料（不延遲，因為這是預錄檔案）
                while True:
                    audio_data = wav_file.readframes(frames_per_chunk)
                    
                    if not audio_data:
                        break
                    
                    # 編碼為 base64
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    # 發送音訊資料
                    event = {
                        "type": "input_audio_buffer.append",
                        "audio": audio_base64
                    }
                    
                    try:
                        await websocket.send(json.dumps(event))
                        bytes_sent += len(audio_data)
                        chunks_sent += 1
                        
                        # 每發送 50 個 chunks 顯示進度
                        if chunks_sent % 50 == 0:
                            progress = (bytes_sent / total_bytes) * 100
                            print(f"發送進度: {progress:.1f}% ({chunks_sent} chunks)")
                    except websockets.exceptions.ConnectionClosed:
                        # WebSocket 已關閉，停止發送
                        print(f"WebSocket 連接已關閉，已發送 {bytes_sent}/{total_bytes} 位元組 ({chunks_sent} chunks)")
                        break
                    
                    # 小延遲避免發送過快導致緩衝區溢出
                    await asyncio.sleep(0.001)  # 1ms 延遲
                
                print(f"音訊發送完成: {bytes_sent}/{total_bytes} 位元組 ({chunks_sent} chunks)")
        
        except websockets.exceptions.ConnectionClosed as e:
            # 連接關閉是正常的（當接收完成時）
            print(f"WebSocket 連接已關閉: {e}")
        except Exception as e:
            print(f"發送音訊時出錯: {e}")
            raise
    
    async def _receive_transcriptions(self, websocket) -> AsyncIterator[Dict[str, Any]]:
        """接收轉錄結果"""
        current_transcript = ""
        start_time = None
        subtitle_id = 0
        last_subtitle_end_time = 0.0
        accumulated_audio_time = 0.0  # 累積的音訊時間（秒）
        
        try:
            async for message in websocket:
                try:
                    event = json.loads(message)
                except json.JSONDecodeError:
                    continue
                
                event_type = event.get("type")
                
                # 轉錄增量更新
                if event_type == "conversation.item.input_audio_transcription.delta":
                    delta = event.get("delta", "")
                    current_transcript += delta
                    
                    # 從事件中取得時間戳（如果有的話）
                    item = event.get("item", {})
                    if "audio_start_ms" in item and start_time is None:
                        start_time = item["audio_start_ms"] / 1000.0
                    elif start_time is None:
                        # 如果沒有時間戳，使用累積時間
                        start_time = accumulated_audio_time
                
                # 轉錄完成
                elif event_type == "conversation.item.input_audio_transcription.completed":
                    item = event.get("item", {})
                    transcript = item.get("transcript", current_transcript)
                    
                    if transcript.strip():
                        subtitle_id += 1
                        
                        # 嘗試從事件中取得時間戳
                        audio_start_ms = item.get("audio_start_ms")
                        audio_end_ms = item.get("audio_end_ms")
                        
                        if audio_start_ms is not None and audio_end_ms is not None:
                            # 使用 API 提供的時間戳
                            start_time = audio_start_ms / 1000.0
                            end_time = audio_end_ms / 1000.0
                            accumulated_audio_time = end_time
                        else:
                            # 如果沒有時間戳，使用估算
                            if start_time is None:
                                start_time = last_subtitle_end_time
                            
                            # 根據文字長度估算持續時間
                            # 中文平均每字約 0.3-0.4 秒，英文平均每字約 0.2-0.3 秒
                            word_count = len(transcript.split())
                            char_count = len(transcript)
                            
                            # 混合估算：考慮中英文混合
                            estimated_duration = max(1.0, word_count * 0.3 + (char_count - word_count) * 0.1)
                            end_time = start_time + estimated_duration
                            accumulated_audio_time = end_time
                        
                        subtitle_data = {
                            "id": subtitle_id,
                            "start_time": max(0.0, start_time),
                            "end_time": end_time,
                            "text": transcript.strip()
                        }
                        
                        print(f"字幕 {subtitle_id}: {subtitle_data['start_time']:.2f}s - {subtitle_data['end_time']:.2f}s ({len(transcript)} 字)")
                        
                        yield subtitle_data
                        
                        # 更新最後一個字幕的結束時間
                        last_subtitle_end_time = end_time
                        
                        # 重置
                        current_transcript = ""
                        start_time = None
                
                # 會話更新事件 - 可能包含音訊進度資訊
                elif event_type == "session.updated":
                    session = event.get("session", {})
                    # 可以從這裡取得音訊進度資訊（如果有）
                
                # 錯誤處理
                elif event_type == "error":
                    error = event.get("error", {})
                    error_msg = error.get("message", "未知錯誤")
                    error_type = error.get("type", "")
                    print(f"API 錯誤 [{error_type}]: {error_msg}")
                    # 不立即 raise，讓接收繼續進行
        
        except websockets.exceptions.ConnectionClosed:
            # 連接關閉是正常的
            pass
        except Exception as e:
            print(f"接收轉錄時出錯: {e}")
            raise


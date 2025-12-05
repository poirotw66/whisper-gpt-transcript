#!/usr/bin/env python3
"""
简单的 OpenAI Realtime API 转录测试
使用麦克风进行实时语音转录
"""

import asyncio
import websockets
import json
import pyaudio
import base64
import os

# 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key-here")
REALTIME_API_URL = "wss://api.openai.com/v1/realtime?model=gpt-realtime-mini-2025-10-06"

# 音频配置
SAMPLE_RATE = 24000
CHUNK_SIZE = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1


async def send_audio(websocket, audio_stream):
    """从麦克风读取音频并发送到 API"""
    print("开始录音...")
    try:
        while True:
            # 读取音频数据
            audio_data = audio_stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # 编码为 base64
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # 发送音频数据
            event = {
                "type": "input_audio_buffer.append",
                "audio": audio_base64
            }
            await websocket.send(json.dumps(event))
            
            await asyncio.sleep(0.01)  # 小延迟
            
    except Exception as e:
        print(f"发送音频时出错: {e}")


async def receive_transcription(websocket):
    """接收并显示转录结果"""
    try:
        async for message in websocket:
            event = json.loads(message)
            event_type = event.get("type")
            
            # 打印所有事件（调试用）
            # print(f"收到事件: {event_type}")
            
            # 转录增量更新
            if event_type == "conversation.item.input_audio_transcription.delta":
                delta = event.get("delta", "")
                print(f"[转录中] {delta}", end="", flush=True)
            
            # 转录完成
            elif event_type == "conversation.item.input_audio_transcription.completed":
                transcript = event.get("transcript", "")
                print(f"\n[完成] {transcript}\n")
            
            # 错误处理
            elif event_type == "error":
                error = event.get("error", {})
                print(f"\n[错误] {error.get('message', '未知错误')}\n")
                
    except Exception as e:
        print(f"接收转录时出错: {e}")


async def main():
    """主函数"""
    # 检查 API 密钥
    if OPENAI_API_KEY == "your-api-key-here":
        print("错误: 请设置 OPENAI_API_KEY 环境变量")
        print("使用: export OPENAI_API_KEY='your-api-key'")
        return
    
    # 初始化音频
    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )
    
    print("正在连接到 OpenAI Realtime API...")
    
    try:
        # 连接到 WebSocket
        async with websockets.connect(
            REALTIME_API_URL,
            additional_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1"
            }
        ) as websocket:
            print("已连接!")
            
            # 配置转录会话
            session_update = {
                "type": "session.update",
                "session": {
                    "input_audio_transcription": {
                        "model": "whisper-1"
                    },
                    "turn_detection": {
                        "type": "server_vad",
                        "threshold": 0.5,
                        "prefix_padding_ms": 300,
                        "silence_duration_ms": 500
                    }
                }
            }
            await websocket.send(json.dumps(session_update))
            print("转录会话已配置")
            print("请开始说话... (按 Ctrl+C 停止)\n")
            
            # 同时运行发送和接收任务
            send_task = asyncio.create_task(send_audio(websocket, stream))
            receive_task = asyncio.create_task(receive_transcription(websocket))
            
            await asyncio.gather(send_task, receive_task)
            
    except KeyboardInterrupt:
        print("\n\n停止转录...")
    except Exception as e:
        print(f"连接错误: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("已关闭音频流")


if __name__ == "__main__":
    print("=" * 60)
    print("OpenAI Realtime API - 实时转录测试")
    print("=" * 60)
    asyncio.run(main())

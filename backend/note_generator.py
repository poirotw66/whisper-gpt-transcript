"""
筆記生成服務 - 使用 GPT-4o 生成影片筆記
"""
import os
from openai import OpenAI


async def generate_notes(transcript_text: str) -> dict:
    """
    根據轉錄文字生成結構化筆記
    
    Args:
        transcript_text: 完整的轉錄文字
        
    Returns:
        包含摘要、重點、關鍵詞的字典
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境變數未設定")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": """你是一個專業的筆記整理助手。請根據提供的影片轉錄文字，生成結構化的筆記。
請以 JSON 格式回應，包含以下欄位：
- summary: 影片摘要（200-300字）
- key_points: 重點整理（3-5個要點，以陣列形式）
- keywords: 關鍵詞（5-10個，以陣列形式）
- insights: 深入見解或補充說明（可選）

請確保回應是有效的 JSON 格式。"""
                },
                {
                    "role": "user",
                    "content": f"請為以下影片轉錄文字生成筆記：\n\n{transcript_text}"
                }
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )
        
        notes_json = response.choices[0].message.content
        import json
        notes = json.loads(notes_json)
        
        return notes
    
    except Exception as e:
        raise Exception(f"筆記生成失敗: {str(e)}")


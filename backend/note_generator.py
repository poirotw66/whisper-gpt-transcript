"""
筆記生成服務 - 使用 GPT 生成影片筆記（支援雙語版本）
"""
import os
import json
from openai import OpenAI


# 筆記生成使用的模型
NOTE_MODEL = "gpt-4o-mini"  # 輕量模型，速度快、成本低


async def generate_notes(transcript_text: str, language: str = "original") -> dict:
    """
    根據轉錄文字生成結構化筆記
    
    Args:
        transcript_text: 完整的轉錄文字
        language: 輸出語言 ("original" 保持原文, "traditional" 繁體中文)
        
    Returns:
        包含摘要、重點、關鍵詞的字典
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境變數未設定")
    
    client = OpenAI(api_key=api_key)
    
    # 根據語言選擇系統提示
    if language == "traditional":
        system_prompt = """你是一個專業的筆記整理助手。請根據提供的影片轉錄文字，生成結構化的筆記。
請以繁體中文輸出，並以 JSON 格式回應，包含以下欄位：
- summary: 影片摘要（200-300字，繁體中文）
- key_points: 重點整理（3-5個要點，以陣列形式，繁體中文）
- keywords: 關鍵詞（5-10個，以陣列形式，繁體中文）
- insights: 深入見解或補充說明（繁體中文，可選）

請確保回應是有效的 JSON 格式，所有內容都使用繁體中文。"""
    else:
        system_prompt = """你是一個專業的筆記整理助手。請根據提供的影片轉錄文字，生成結構化的筆記。

重要：請使用與輸入文字相同的語言輸出。
- 如果輸入是日文，請用日文輸出
- 如果輸入是英文，請用英文輸出
- 如果輸入是中文，請用中文輸出
- 不要翻譯，保持原文語言

請以 JSON 格式回應，包含以下欄位：
- summary: 影片摘要（200-300字，使用原文語言）
- key_points: 重點整理（3-5個要點，以陣列形式，使用原文語言）
- keywords: 關鍵詞（5-10個，以陣列形式，使用原文語言）
- insights: 深入見解或補充說明（使用原文語言，可選）

請確保回應是有效的 JSON 格式。"""
    
    try:
        response = client.chat.completions.create(
            model=NOTE_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
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
        notes = json.loads(notes_json)
        
        return notes
    
    except Exception as e:
        raise Exception(f"筆記生成失敗: {str(e)}")


async def generate_bilingual_notes(transcript_text: str) -> dict:
    """
    生成雙語版本的筆記（原文 + 繁體中文）
    
    Args:
        transcript_text: 完整的轉錄文字
        
    Returns:
        包含 original 和 traditional 兩個版本的字典
    """
    # 並行生成兩種版本
    import asyncio
    
    original_task = generate_notes(transcript_text, "original")
    traditional_task = generate_notes(transcript_text, "traditional")
    
    original_notes, traditional_notes = await asyncio.gather(
        original_task, traditional_task,
        return_exceptions=True
    )
    
    result = {
        "original": original_notes if not isinstance(original_notes, Exception) else None,
        "traditional": traditional_notes if not isinstance(traditional_notes, Exception) else None
    }
    
    # 如果原文生成失敗但繁中成功，使用繁中作為備用
    if result["original"] is None and result["traditional"] is not None:
        result["original"] = result["traditional"]
    # 如果繁中生成失敗但原文成功，使用原文作為備用
    elif result["traditional"] is None and result["original"] is not None:
        result["traditional"] = result["original"]
    
    return result


"""
翻譯服務 - 將文字翻譯為繁體中文
"""
import os
from openai import OpenAI


async def translate_to_traditional_chinese(text: str) -> str:
    """
    將文字翻譯為繁體中文
    
    Args:
        text: 要翻譯的文字
        
    Returns:
        翻譯後的繁體中文文字
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY 環境變數未設定")
    
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是一個專業的翻譯助手，專門將各種語言翻譯成繁體中文。請保持原文的語調和風格，只翻譯內容，不要添加任何解釋或註釋。"
                },
                {
                    "role": "user",
                    "content": f"請將以下文字翻譯成繁體中文：\n\n{text}"
                }
            ],
            temperature=0.3
        )
        
        translated_text = response.choices[0].message.content.strip()
        return translated_text
    
    except Exception as e:
        raise Exception(f"翻譯失敗: {str(e)}")


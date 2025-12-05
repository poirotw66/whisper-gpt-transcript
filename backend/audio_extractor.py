"""
音訊提取模組 - 使用 FFmpeg 從影片提取音訊
"""
import subprocess
import os
from pathlib import Path


def extract_audio(video_path: str, output_path: str, sample_rate: int = 24000):
    """
    從影片檔案提取音訊並轉換為 24kHz PCM WAV 格式
    
    Args:
        video_path: 輸入影片路徑
        output_path: 輸出音訊路徑
        sample_rate: 採樣率 (預設 24000 Hz)
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"影片檔案不存在: {video_path}")
    
    # 檢查 FFmpeg 是否可用
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("FFmpeg 未安裝或不在 PATH 中。請先安裝 FFmpeg。")
    
    # 使用 FFmpeg 提取音訊
    # -i: 輸入檔案
    # -vn: 不包含視訊
    # -ar: 採樣率
    # -ac: 聲道數 (1 = mono)
    # -f: 輸出格式 (wav)
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # 不包含視訊
        "-ar", str(sample_rate),  # 採樣率
        "-ac", "1",  # 單聲道
        "-f", "wav",  # WAV 格式
        "-y",  # 覆蓋輸出檔案
        output_path
    ]
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return output_path
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"FFmpeg 執行失敗: {e.stderr}")


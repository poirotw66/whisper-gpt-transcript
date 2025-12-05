# OpenAI Realtime API 转录测试

简单的实时语音转录测试程序。

## 安装依赖

```bash
pip install -r requirements.txt
```

### macOS 上安装 PyAudio

如果遇到安装问题，请先安装 portaudio:

```bash
brew install portaudio
pip install pyaudio
```

## 设置 API 密钥

```bash
export OPENAI_API_KEY='your-api-key-here'
```

## 运行

```bash
python transcription_test.py
```

## 使用说明

1. 运行程序后，它会自动开启麦克风
2. 开始说话，程序会实时显示转录结果
3. 按 `Ctrl+C` 停止

## 功能特点

- ✅ 实时语音转录
- ✅ 自动语音活动检测 (VAD)
- ✅ 增量转录显示
- ✅ 使用 `gpt-4o-transcribe` 模型
- ✅ 24kHz PCM 音频格式

## 注意事项

- 需要有效的 OpenAI API 密钥
- 需要麦克风权限
- 网络连接必须稳定

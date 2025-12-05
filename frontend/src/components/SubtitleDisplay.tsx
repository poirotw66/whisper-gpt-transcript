import { useEffect, useRef } from 'react'

interface Subtitle {
  id: number
  start_time: number
  end_time: number
  text: string
  translated_text?: string
}

interface SubtitleDisplayProps {
  subtitles: Subtitle[]
  language: 'original' | 'traditional'
  isTranscribing: boolean
}

export default function SubtitleDisplay({
  subtitles,
  language,
  isTranscribing
}: SubtitleDisplayProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // 自動滾動到最新字幕
    if (containerRef.current && subtitles.length > 0) {
      const lastSubtitle = containerRef.current.lastElementChild
      if (lastSubtitle) {
        lastSubtitle.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
    }
  }, [subtitles])

  const getSubtitleText = (subtitle: Subtitle) => {
    if (language === 'traditional' && subtitle.translated_text) {
      return subtitle.translated_text
    }
    return subtitle.text
  }

  if (subtitles.length === 0 && !isTranscribing) {
    return (
      <div className="text-center py-12 text-gray-400">
        <p>尚未有字幕，請播放影片開始轉錄</p>
      </div>
    )
  }

  return (
    <div
      ref={containerRef}
      className="max-h-96 overflow-y-auto space-y-2"
    >
      {subtitles.map((subtitle) => (
        <div
          key={subtitle.id}
          className="p-3 bg-gray-50 rounded-lg border border-gray-200 hover:bg-gray-100 transition-colors"
        >
          <div className="flex items-start justify-between gap-4">
            <p className="text-gray-800 flex-1">
              {getSubtitleText(subtitle)}
            </p>
            <span className="text-xs text-gray-500 whitespace-nowrap">
              {formatTime(subtitle.start_time)} → {formatTime(subtitle.end_time)}
            </span>
          </div>
          {language === 'traditional' && subtitle.translated_text && (
            <p className="text-sm text-gray-500 mt-1 italic">
              {subtitle.text}
            </p>
          )}
        </div>
      ))}
      
      {isTranscribing && (
        <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-blue-600 rounded-full animate-pulse"></div>
            <span className="text-sm text-blue-600">轉錄中...</span>
          </div>
        </div>
      )}
    </div>
  )
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}


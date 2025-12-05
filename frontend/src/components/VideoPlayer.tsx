import { useEffect, useRef, useState } from 'react'
import { Play, Pause, Loader2 } from 'lucide-react'
import useWebSocket from '../hooks/useWebSocket'

interface Subtitle {
  id: number
  start_time: number
  end_time: number
  text: string
  translated_text?: string
}

interface VideoPlayerProps {
  videoUrl: string
  videoId: string
  subtitles: Subtitle[]
  language: 'original' | 'traditional'
  onSubtitleReceived: (subtitle: any) => void
  onTranscriptionStart: () => void
  onTranscriptionComplete: () => void
  onNotesReceived?: (notes: any) => void
  onEnded: () => void
}

export default function VideoPlayer({
  videoUrl,
  videoId,
  subtitles,
  language,
  onSubtitleReceived,
  onTranscriptionStart,
  onTranscriptionComplete,
  onNotesReceived,
  onEnded
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [hasStarted, setHasStarted] = useState(false)
  const [currentSubtitle, setCurrentSubtitle] = useState<Subtitle | null>(null)
  const wsRef = useRef<{ connect: () => void; disconnect: () => void } | null>(null)

  const { connect, disconnect, connected } = useWebSocket(
    `/ws/transcribe/${videoId}`,
    {
      onMessage: (data: any) => {
        console.log('WebSocket 收到消息:', data.type)
        if (data.type === 'status') {
          console.log('狀態:', data.message)
        } else if (data.type === 'subtitle') {
          console.log('收到字幕:', data.data)
          onSubtitleReceived(data.data)
        } else if (data.type === 'completed') {
          console.log('轉錄完成')
          setIsTranscribing(false)
          onTranscriptionComplete()
          // 延遲斷開連接，等待筆記生成
          setTimeout(() => {
            disconnect()
            wsRef.current = null
          }, 2000)
        } else if (data.type === 'notes') {
          console.log('收到筆記')
          if (onNotesReceived) {
            onNotesReceived(data.data)
          }
        } else if (data.type === 'error') {
          console.error('轉錄錯誤:', data.error)
          setIsTranscribing(false)
          disconnect()
          wsRef.current = null
        }
      },
      reconnect: false
    }
  )

  // 儲存 WebSocket 連接函數的引用
  useEffect(() => {
    wsRef.current = { connect, disconnect }
  }, [connect, disconnect])

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  // 根據影片播放時間更新當前字幕
  useEffect(() => {
    const video = videoRef.current
    if (!video) return

    const updateSubtitle = () => {
      const currentTime = video.currentTime
      
      // 找到當前時間對應的字幕
      const activeSubtitle = subtitles.find(
        (subtitle) => 
          currentTime >= subtitle.start_time && 
          currentTime <= subtitle.end_time
      )
      
      setCurrentSubtitle(activeSubtitle || null)
    }

    video.addEventListener('timeupdate', updateSubtitle)
    return () => {
      video.removeEventListener('timeupdate', updateSubtitle)
    }
  }, [subtitles])

  const handlePlay = () => {
    if (videoRef.current) {
      if (!hasStarted && !isTranscribing) {
        // 第一次播放時開始轉錄，且確保沒有正在進行的轉錄
        setHasStarted(true)
        setIsTranscribing(true)
        onTranscriptionStart()
        if (wsRef.current) {
          wsRef.current.connect()
        } else {
          connect()
        }
      }
      videoRef.current.play()
      setIsPlaying(true)
    }
  }

  const handlePause = () => {
    if (videoRef.current) {
      videoRef.current.pause()
      setIsPlaying(false)
    }
  }

  const handleEnded = () => {
    setIsPlaying(false)
    // 不要在影片結束時斷開連接，等待轉錄完成
    // Whisper API 是一次性處理，需要等待結果返回
    if (!isTranscribing) {
      disconnect()
    }
    onEnded()
  }

  const getSubtitleText = (subtitle: Subtitle | null) => {
    if (!subtitle) return null
    if (language === 'traditional' && subtitle.translated_text) {
      return subtitle.translated_text
    }
    return subtitle.text
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <div className="relative bg-black aspect-video">
        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full"
          onEnded={handleEnded}
          controls
        />
        
        {/* 即時字幕疊加顯示 */}
        {currentSubtitle && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/60 to-transparent px-4 py-6">
            <p className="text-white text-lg font-medium text-center drop-shadow-lg">
              {getSubtitleText(currentSubtitle)}
            </p>
          </div>
        )}
        
        {isTranscribing && (
          <div className="absolute top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm font-medium">轉錄中...</span>
          </div>
        )}
      </div>

      <div className="p-4 bg-gray-50 border-t">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {isPlaying ? (
              <button
                onClick={handlePause}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Pause className="w-5 h-5" />
              </button>
            ) : (
              <button
                onClick={handlePlay}
                className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <Play className="w-5 h-5" />
              </button>
            )}
            <span className="text-sm text-gray-600">
              {hasStarted ? '轉錄已開始' : '點擊播放開始轉錄'}
            </span>
          </div>
          {connected && (
            <span className="text-xs text-green-600 bg-green-50 px-2 py-1 rounded">
              已連接
            </span>
          )}
        </div>
      </div>
    </div>
  )
}


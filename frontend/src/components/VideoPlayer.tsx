import { useEffect, useRef, useState } from 'react'
import { Play, Pause, Loader2 } from 'lucide-react'
import useWebSocket from '../hooks/useWebSocket'

interface VideoPlayerProps {
  videoUrl: string
  videoId: string
  onSubtitleReceived: (subtitle: any) => void
  onTranscriptionStart: () => void
  onTranscriptionComplete: () => void
  onEnded: () => void
}

export default function VideoPlayer({
  videoUrl,
  videoId,
  onSubtitleReceived,
  onTranscriptionStart,
  onTranscriptionComplete,
  onEnded
}: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [hasStarted, setHasStarted] = useState(false)

  const { connect, disconnect, connected } = useWebSocket(
    `/ws/transcribe/${videoId}`,
    {
      onMessage: (data: any) => {
        if (data.type === 'subtitle') {
          onSubtitleReceived(data.data)
        } else if (data.type === 'completed') {
          setIsTranscribing(false)
          onTranscriptionComplete()
        } else if (data.type === 'error') {
          console.error('轉錄錯誤:', data.error)
          setIsTranscribing(false)
        }
      }
    }
  )

  useEffect(() => {
    return () => {
      disconnect()
    }
  }, [disconnect])

  const handlePlay = () => {
    if (videoRef.current) {
      if (!hasStarted) {
        // 第一次播放時開始轉錄
        setHasStarted(true)
        setIsTranscribing(true)
        onTranscriptionStart()
        connect()
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
    disconnect()
    onEnded()
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


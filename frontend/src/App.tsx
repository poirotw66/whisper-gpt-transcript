import { useState } from 'react'
import VideoUploader from './components/VideoUploader'
import VideoPlayer from './components/VideoPlayer'
import SubtitleDisplay from './components/SubtitleDisplay'
import LanguageSelector from './components/LanguageSelector'
import ExportButton from './components/ExportButton'
import NotesPanel from './components/NotesPanel'
import { Video } from 'lucide-react'

interface Subtitle {
  id: number
  start_time: number
  end_time: number
  text: string
  translated_text?: string
}

interface Notes {
  summary?: string
  key_points?: string[]
  keywords?: string[]
  insights?: string
}

function App() {
  const [videoId, setVideoId] = useState<string | null>(null)
  const [videoUrl, setVideoUrl] = useState<string | null>(null)
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [language, setLanguage] = useState<'original' | 'traditional'>('original')
  const [isTranscribing, setIsTranscribing] = useState(false)
  const [notes, setNotes] = useState<Notes | null>(null)
  const [showNotes, setShowNotes] = useState(false)

  const handleVideoUploaded = (id: string, url: string) => {
    setVideoId(id)
    setVideoUrl(url)
    setSubtitles([])
    setNotes(null)
    setShowNotes(false)
  }

  const handleSubtitleReceived = (subtitle: Subtitle) => {
    setSubtitles(prev => [...prev, subtitle])
  }

  const handleTranscriptionStart = () => {
    setIsTranscribing(true)
  }

  const handleTranscriptionComplete = async () => {
    setIsTranscribing(false)
    // 自動生成筆記
    if (videoId) {
      try {
        const response = await fetch(`/api/generate-notes/${videoId}`, {
          method: 'POST'
        })
        const data = await response.json()
        if (data.notes) {
          setNotes(data.notes)
        }
      } catch (error) {
        console.error('生成筆記失敗:', error)
      }
    }
  }

  const handleTranslateRequest = async () => {
    if (!videoId) return
    
    try {
      const response = await fetch(`/api/translate/${videoId}`, {
        method: 'POST'
      })
      const data = await response.json()
      
      if (response.ok) {
        // 重新載入字幕資料以取得翻譯
        const subtitleResponse = await fetch(`/api/subtitles/${videoId}?language=traditional`)
        const subtitleData = await subtitleResponse.json()
        if (subtitleData.subtitles) {
          // 更新字幕列表，合併翻譯
          setSubtitles(prev => {
            const translatedMap = new Map(
              subtitleData.subtitles.map((s: any) => [s.id, s.translated_text])
            )
            return prev.map(s => ({
              ...s,
              translated_text: translatedMap.get(s.id) || s.translated_text
            }))
          })
        }
      } else {
        console.error('翻譯失敗:', data.error)
      }
    } catch (error) {
      console.error('翻譯請求失敗:', error)
    }
  }

  const handleVideoEnded = () => {
    // 影片播放完畢後自動生成筆記
    if (videoId && subtitles.length > 0 && !notes) {
      handleTranscriptionComplete()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2 flex items-center gap-3">
            <Video className="w-10 h-10 text-blue-600" />
            影片即時字幕生成器
          </h1>
          <p className="text-gray-600">上傳影片，自動生成即時字幕與筆記</p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 左側：影片上傳與播放 */}
          <div className="lg:col-span-2 space-y-6">
            {!videoId ? (
              <VideoUploader onUploaded={handleVideoUploaded} />
            ) : (
              <>
                <VideoPlayer
                  videoUrl={videoUrl!}
                  videoId={videoId}
                  onSubtitleReceived={handleSubtitleReceived}
                  onTranscriptionStart={handleTranscriptionStart}
                  onTranscriptionComplete={handleTranscriptionComplete}
                  onEnded={handleVideoEnded}
                />
                
                <div className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-semibold text-gray-800">字幕</h2>
                    <div className="flex items-center gap-4">
                      <LanguageSelector
                        language={language}
                        onLanguageChange={setLanguage}
                        hasTranslated={subtitles.some(s => s.translated_text)}
                        videoId={videoId}
                        onTranslateRequest={handleTranslateRequest}
                      />
                      <ExportButton
                        videoId={videoId}
                        language={language}
                        disabled={subtitles.length === 0}
                      />
                    </div>
                  </div>
                  <SubtitleDisplay
                    subtitles={subtitles}
                    language={language}
                    isTranscribing={isTranscribing}
                  />
                </div>
              </>
            )}
          </div>

          {/* 右側：筆記面板 */}
          <div className="lg:col-span-1">
            <NotesPanel
              notes={notes}
              showNotes={showNotes}
              onToggleNotes={() => setShowNotes(!showNotes)}
            />
          </div>
        </div>
      </div>
    </div>
  )
}

export default App


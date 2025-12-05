import { useState } from 'react'
import { Upload, Loader2 } from 'lucide-react'

interface VideoUploaderProps {
  onUploaded: (videoId: string, videoUrl: string) => void
}

export default function VideoUploader({ onUploaded }: VideoUploaderProps) {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    // 檢查檔案類型
    if (!file.type.startsWith('video/')) {
      setError('請選擇有效的影片檔案')
      return
    }

    // 檢查檔案大小 (500MB)
    if (file.size > 500 * 1024 * 1024) {
      setError('檔案大小不能超過 500MB')
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '上傳失敗')
      }

      const videoUrl = `/api/video/${data.video_id}`
      onUploaded(data.video_id, videoUrl)
    } catch (err) {
      setError(err instanceof Error ? err.message : '上傳失敗')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-8">
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-blue-500 transition-colors">
        <input
          type="file"
          id="video-upload"
          accept="video/*"
          onChange={handleFileChange}
          disabled={uploading}
          className="hidden"
        />
        <label
          htmlFor="video-upload"
          className="cursor-pointer flex flex-col items-center gap-4"
        >
          {uploading ? (
            <>
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin" />
              <span className="text-lg text-gray-600">上傳中...</span>
            </>
          ) : (
            <>
              <Upload className="w-16 h-16 text-gray-400" />
              <div>
                <span className="text-lg font-semibold text-blue-600">
                  點擊上傳影片
                </span>
                <p className="text-sm text-gray-500 mt-2">
                  或拖放影片檔案到此處
                </p>
                <p className="text-xs text-gray-400 mt-1">
                  支援 MP4, MOV, AVI 等格式，最大 500MB
                </p>
              </div>
            </>
          )}
        </label>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}
    </div>
  )
}


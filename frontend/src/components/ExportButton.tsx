import { Download } from 'lucide-react'
import { useState } from 'react'

interface ExportButtonProps {
  videoId: string
  language: 'original' | 'traditional'
  disabled: boolean
}

export default function ExportButton({
  videoId,
  language,
  disabled
}: ExportButtonProps) {
  const [exporting, setExporting] = useState(false)

  const handleExport = async () => {
    if (disabled) return

    setExporting(true)
    try {
      const response = await fetch(`/api/export/srt/${videoId}?language=${language}`)
      
      if (!response.ok) {
        throw new Error('匯出失敗')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `subtitle_${language}.srt`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('匯出失敗:', error)
      alert('匯出失敗，請稍後再試')
    } finally {
      setExporting(false)
    }
  }

  return (
    <button
      onClick={handleExport}
      disabled={disabled || exporting}
      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
    >
      <Download className="w-4 h-4" />
      <span>{exporting ? '匯出中...' : '匯出 SRT'}</span>
    </button>
  )
}


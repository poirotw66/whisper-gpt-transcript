import { useState } from 'react'
import { FileText, ChevronDown, ChevronUp, Languages } from 'lucide-react'

interface SingleNotes {
  summary?: string
  key_points?: string[]
  keywords?: string[]
  insights?: string
}

interface BilingualNotes {
  original?: SingleNotes | null
  traditional?: SingleNotes | null
}

interface NotesPanelProps {
  notes: BilingualNotes | null
  showNotes: boolean
  onToggleNotes: () => void
}

export default function NotesPanel({
  notes,
  showNotes,
  onToggleNotes
}: NotesPanelProps) {
  const [notesLanguage, setNotesLanguage] = useState<'original' | 'traditional'>('original')

  if (!notes) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 text-gray-500">
          <FileText className="w-5 h-5" />
          <span className="text-sm">影片播放完畢後將自動生成筆記</span>
        </div>
      </div>
    )
  }

  // 取得當前語言的筆記
  const currentNotes = notesLanguage === 'traditional' ? notes.traditional : notes.original

  if (!currentNotes) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center gap-2 text-gray-500">
          <FileText className="w-5 h-5" />
          <span className="text-sm">筆記生成中...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      <button
        onClick={onToggleNotes}
        className="w-full p-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white flex items-center justify-between hover:from-purple-700 hover:to-blue-700 transition-colors"
      >
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          <span className="font-semibold">影片筆記</span>
        </div>
        {showNotes ? (
          <ChevronUp className="w-5 h-5" />
        ) : (
          <ChevronDown className="w-5 h-5" />
        )}
      </button>

      {showNotes && (
        <div className="p-6 space-y-6 max-h-[calc(100vh-200px)] overflow-y-auto">
          {/* 語言切換 */}
          <div className="flex items-center justify-between border-b pb-4">
            <div className="flex items-center gap-2 text-gray-600">
              <Languages className="w-4 h-4" />
              <span className="text-sm">筆記語言</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setNotesLanguage('original')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  notesLanguage === 'original'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                原文
              </button>
              <button
                onClick={() => setNotesLanguage('traditional')}
                className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                  notesLanguage === 'traditional'
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                繁體中文
              </button>
            </div>
          </div>

          {currentNotes.summary && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">摘要</h3>
              <p className="text-gray-600 leading-relaxed">{currentNotes.summary}</p>
            </div>
          )}

          {currentNotes.key_points && currentNotes.key_points.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">重點整理</h3>
              <ul className="space-y-2">
                {currentNotes.key_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="text-blue-600 font-bold mt-1">•</span>
                    <span className="text-gray-600 flex-1">{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {currentNotes.keywords && currentNotes.keywords.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">關鍵詞</h3>
              <div className="flex flex-wrap gap-2">
                {currentNotes.keywords.map((keyword, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            </div>
          )}

          {currentNotes.insights && (
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-2">深入見解</h3>
              <p className="text-gray-600 leading-relaxed">{currentNotes.insights}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}


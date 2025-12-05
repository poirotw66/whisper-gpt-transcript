import { Languages } from 'lucide-react'

interface LanguageSelectorProps {
  language: 'original' | 'traditional'
  onLanguageChange: (lang: 'original' | 'traditional') => void
  hasTranslated: boolean
  videoId: string | null
  onTranslateRequest?: () => void
}

export default function LanguageSelector({
  language,
  onLanguageChange,
  hasTranslated,
  videoId,
  onTranslateRequest
}: LanguageSelectorProps) {
  const handleLanguageChange = async (newLang: 'original' | 'traditional') => {
    if (newLang === 'traditional' && !hasTranslated && videoId && onTranslateRequest) {
      // 如果切換到繁體中文但尚未翻譯，觸發翻譯
      onTranslateRequest()
    }
    onLanguageChange(newLang)
  }

  return (
    <div className="flex items-center gap-2">
      <Languages className="w-4 h-4 text-gray-600" />
      <select
        value={language}
        onChange={(e) => handleLanguageChange(e.target.value as 'original' | 'traditional')}
        className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="original">原文</option>
        <option value="traditional">
          繁體中文 {!hasTranslated && '(翻譯中...)'}
        </option>
      </select>
    </div>
  )
}


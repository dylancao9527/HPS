import { Sun, Moon } from 'lucide-react'
import { useTheme } from '@/hooks/useTheme'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()

  return (
    <button className="theme-toggle" onClick={toggleTheme} title="切换主题">
      {theme === 'light' ? <Moon size={18} /> : <Sun size={18} />}
    </button>
  )
}

import type { KeyboardEvent } from 'react'

export interface PredictionTab {
  key: string
  label: string
}

interface PredictionResultTabsProps {
  tabs: PredictionTab[]
  activeTab: string
  onChange: (key: string) => void
}

export default function PredictionResultTabs({ tabs, activeTab, onChange }: PredictionResultTabsProps) {
  const handleKeyDown = (event: KeyboardEvent<HTMLButtonElement>, index: number) => {
    const lastIndex = tabs.length - 1
    let nextIndex = index

    if (event.key === 'ArrowRight') nextIndex = index === lastIndex ? 0 : index + 1
    if (event.key === 'ArrowLeft') nextIndex = index === 0 ? lastIndex : index - 1
    if (event.key === 'Home') nextIndex = 0
    if (event.key === 'End') nextIndex = lastIndex

    if (nextIndex === index) return

    event.preventDefault()
    onChange(tabs[nextIndex].key)
    document.getElementById(`prediction-tab-${tabs[nextIndex].key}`)?.focus()
  }

  return (
    <div className="prediction-results-nav" role="tablist" aria-label="预测结果导航">
      {tabs.map((tab, index) => (
        <button
          key={tab.key}
          id={`prediction-tab-${tab.key}`}
          type="button"
          role="tab"
          tabIndex={activeTab === tab.key ? 0 : -1}
          aria-selected={activeTab === tab.key}
          aria-controls={`prediction-panel-${tab.key}`}
          className={`prediction-results-tab ${activeTab === tab.key ? 'is-active' : ''}`}
          onClick={() => onChange(tab.key)}
          onKeyDown={(event) => handleKeyDown(event, index)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

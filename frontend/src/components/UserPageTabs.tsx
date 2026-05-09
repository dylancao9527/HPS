import { useEffect, useRef } from 'react'
import type { KeyboardEvent } from 'react'

interface UserPageTabItem {
  key: string
  label: string
}

interface UserPageTabsProps {
  tabs: UserPageTabItem[]
  activeKey: string
  onChange: (key: string) => void
  idPrefix?: string
  focusOnActiveKeyChange?: boolean
}

export default function UserPageTabs({
  tabs,
  activeKey,
  onChange,
  idPrefix = 'user-page',
  focusOnActiveKeyChange = false,
}: UserPageTabsProps) {
  const previousActiveKeyRef = useRef(activeKey)

  useEffect(() => {
    if (!focusOnActiveKeyChange) {
      previousActiveKeyRef.current = activeKey
      return
    }

    if (previousActiveKeyRef.current === activeKey) return

    previousActiveKeyRef.current = activeKey
    document.getElementById(`${idPrefix}-tab-${activeKey}`)?.focus()
  }, [activeKey, focusOnActiveKeyChange, idPrefix])

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
    document.getElementById(`${idPrefix}-tab-${tabs[nextIndex].key}`)?.focus()
  }

  return (
    <div className="user-page-tabs" role="tablist" aria-label="页面分区导航">
      {tabs.map((tab, index) => (
        <button
          key={tab.key}
          id={`${idPrefix}-tab-${tab.key}`}
          type="button"
          role="tab"
          tabIndex={activeKey === tab.key ? 0 : -1}
          aria-selected={activeKey === tab.key}
          aria-controls={`${idPrefix}-panel-${tab.key}`}
          className={`user-page-tab${activeKey === tab.key ? ' is-active' : ''}`}
          onClick={() => onChange(tab.key)}
          onKeyDown={(event) => handleKeyDown(event, index)}
        >
          {tab.label}
        </button>
      ))}
    </div>
  )
}

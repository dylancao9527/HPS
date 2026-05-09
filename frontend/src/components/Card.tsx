import { createElement } from 'react'
import type { ElementType, ReactNode } from 'react'

interface CardProps {
  title?: ReactNode
  children: ReactNode
  className?: string
  titleAs?: ElementType
}

export default function Card({ title, children, className = '', titleAs = 'div' }: CardProps) {
  return (
    <div className={`card ${className}`}>
      {title && createElement(titleAs, { className: 'card-title' }, title)}
      {children}
    </div>
  )
}

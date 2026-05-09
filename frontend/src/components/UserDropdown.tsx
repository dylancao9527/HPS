import { useState, useRef, useEffect } from 'react'
import type { MouseEvent as ReactMouseEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { ChevronDown, ChevronUp, User, LogOut } from 'lucide-react'

export default function UserDropdown() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const handler = (event: MouseEvent) => {
      const target = event.target
      if (ref.current && target instanceof Node && !ref.current.contains(target)) {
        setOpen(false)
      }
    }

    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [])

  if (!user) return null

  const handleProfileClick = (event: ReactMouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setOpen(false)
    navigate('/profile')
  }

  const handleLogoutClick = (event: ReactMouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    setOpen(false)
    logout()
    navigate('/login')
  }

  return (
    <div className="user-dropdown" ref={ref}>
      <button className="user-dropdown-trigger" type="button" aria-haspopup="menu" aria-expanded={open} onClick={() => setOpen(!open)}>
        {user.avatar ? (
          <img src={user.avatar} alt="" className="user-avatar user-avatar-image" />
        ) : (
          <span className="user-avatar">{user.username[0].toUpperCase()}</span>
        )}
        <span className="user-dropdown-name">{user.nickname || user.username}</span>
        <span className="user-dropdown-arrow">
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </span>
      </button>
      {open && (
        <div className="user-dropdown-menu">
          <button onClick={handleProfileClick}>
            <User size={16} /> 个人中心
          </button>
          <button onClick={handleLogoutClick}>
            <LogOut size={16} /> 退出登录
          </button>
        </div>
      )}
    </div>
  )
}

import { useEffect, useRef, useState } from 'react'
import type { ChangeEvent } from 'react'

function generateCode(length = 4) {
  const chars = 'abcdefghjkmnpqrstuvwxyz23456789'
  let code = ''
  for (let i = 0; i < length; i++) {
    code += chars[Math.floor(Math.random() * chars.length)]
  }
  return code
}

interface CaptchaProps {
  onValid: (valid: boolean) => void
}

export default function Captcha({ onValid }: CaptchaProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const [code, setCode] = useState<string>(() => generateCode())
  const [input, setInput] = useState('')

  useEffect(() => {
    drawCaptcha(canvasRef.current, code)
  }, [code])

  useEffect(() => {
    onValid(false)
  }, [code, onValid])

  const refresh = () => {
    setCode(generateCode())
    setInput('')
  }

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value
    setInput(val)
    onValid(val.toLowerCase() === code.toLowerCase())
  }

  return (
    <div className="captcha-wrapper">
      <input
        type="text"
        value={input}
        onChange={handleChange}
        placeholder="请输入验证码"
        maxLength={4}
        autoComplete="off"
      />
      <canvas
        ref={canvasRef}
        width={120}
        height={38}
        className="captcha-canvas"
        onClick={refresh}
        title="点击刷新验证码"
      />
    </div>
  )
}

function drawCaptcha(canvas: HTMLCanvasElement | null, code: string) {
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  const w = canvas.width
  const h = canvas.height

  ctx.fillStyle = getComputedStyle(document.documentElement)
    .getPropertyValue('--card-bg').trim() || '#1e293b'
  ctx.fillRect(0, 0, w, h)

  for (let i = 0; i < 4; i++) {
    ctx.beginPath()
    ctx.moveTo(Math.random() * w, Math.random() * h)
    ctx.lineTo(Math.random() * w, Math.random() * h)
    ctx.strokeStyle = `hsl(${Math.random() * 360}, 50%, 50%)`
    ctx.lineWidth = 0.5
    ctx.stroke()
  }

  for (let i = 0; i < 30; i++) {
    ctx.beginPath()
    ctx.arc(Math.random() * w, Math.random() * h, 1, 0, Math.PI * 2)
    ctx.fillStyle = `hsl(${Math.random() * 360}, 50%, 60%)`
    ctx.fill()
  }

  const colors = ['#6366f1', '#06b6d4', '#f59e0b', '#22c55e', '#ef4444']
  ctx.textBaseline = 'middle'
  for (let i = 0; i < code.length; i++) {
    ctx.save()
    const x = 15 + i * 25
    const y = h / 2 + (Math.random() - 0.5) * 10
    ctx.translate(x, y)
    ctx.rotate((Math.random() - 0.5) * 0.5)
    ctx.font = `bold ${18 + Math.random() * 6}px monospace`
    ctx.fillStyle = colors[i % colors.length]
    const char = code[i]
    if (char) ctx.fillText(char, 0, 0)
    ctx.restore()
  }
}

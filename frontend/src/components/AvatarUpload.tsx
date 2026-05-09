import { useRef } from 'react'
import type { ChangeEvent } from 'react'
import { ImagePlus } from 'lucide-react'
import { useFeedback } from '@/hooks/useFeedback'

interface AvatarUploadProps {
  value?: string | null
  onChange: (value: string) => void
}

export default function AvatarUpload({ value, onChange }: AvatarUploadProps) {
  const inputRef = useRef<HTMLInputElement | null>(null)
  const { showToast } = useFeedback()
  const preview = value || ''

  const handleFile = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    if (!file.type.startsWith('image/')) {
      showToast('请选择图片文件', 'error')
      return
    }

    const reader = new FileReader()
    reader.onload = (ev) => {
      const result = ev.target?.result
      if (typeof result !== 'string') return

      const img = new Image()
      img.onload = () => {
        const canvas = document.createElement('canvas')
        const size = 200
        canvas.width = size
        canvas.height = size
        const ctx = canvas.getContext('2d')
        if (!ctx) return

        const minDim = Math.min(img.width, img.height)
        const sx = (img.width - minDim) / 2
        const sy = (img.height - minDim) / 2

        ctx.drawImage(img, sx, sy, minDim, minDim, 0, 0, size, size)

        const base64 = canvas.toDataURL('image/jpeg', 0.8)
        onChange(base64)
      }
      img.src = result
    }
    reader.readAsDataURL(file)
    e.target.value = ''
  }

  return (
    <div className="avatar-upload" onClick={() => inputRef.current?.click()}>
      {preview ? (
        <img src={preview} alt="头像" className="avatar-preview" />
      ) : (
        <div className="avatar-placeholder">
          <ImagePlus size={28} />
          <span>上传头像</span>
        </div>
      )}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        onChange={handleFile}
        className="avatar-upload-input"
      />
    </div>
  )
}

const PALETTE = [
  { bg: '#f2e9d8', fg: '#1a1a1a' },
  { bg: '#d6482f', fg: '#fdf4ea' },
  { bg: '#1f7a73', fg: '#fdf4ea' },
  { bg: '#1c2b4a', fg: '#fdf4ea' },
  { bg: '#4a2f6b', fg: '#fdf4ea' },
  { bg: '#f2b705', fg: '#1a1a1a' },
  { bg: '#e8793a', fg: '#1a1a1a' },
]

function hashString(value: string): number {
  let hash = 0
  for (let i = 0; i < value.length; i++) {
    hash = (hash << 5) - hash + value.charCodeAt(i)
    hash |= 0
  }
  return Math.abs(hash)
}

interface BookCoverProps {
  title: string
  authorName?: string
  imageUrl?: string | null
  className?: string
  /** Use smaller type for narrow thumbnails (cart lines, order cards). */
  compact?: boolean
}

export function BookCover({ title, authorName, imageUrl, className, compact }: BookCoverProps) {
  if (imageUrl) {
    return (
      <img
        src={imageUrl}
        alt={title}
        className={`h-full w-full rounded-lg object-cover ${className ?? ''}`}
      />
    )
  }

  const { bg, fg } = PALETTE[hashString(title) % PALETTE.length]

  return (
    <div
      className={`flex h-full w-full flex-col justify-between rounded-lg ${compact ? 'p-2' : 'p-4'} ${className ?? ''}`}
      style={{ backgroundColor: bg, color: fg }}
    >
      <p
        className={`line-clamp-4 font-extrabold uppercase leading-tight ${compact ? 'text-xs' : 'text-lg'}`}
      >
        {title}
      </p>
      {authorName && (
        <p
          className={`truncate font-semibold uppercase tracking-wide opacity-80 ${compact ? 'text-[10px]' : 'text-xs'}`}
        >
          {authorName}
        </p>
      )}
    </div>
  )
}

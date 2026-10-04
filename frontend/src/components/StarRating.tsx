import { StarIcon } from '@/components/icons'

interface StarRatingProps {
  value: number
  onChange?: (value: number) => void
  size?: number
}

export function StarRating({ value, onChange, size = 20 }: StarRatingProps) {
  const stars = [1, 2, 3, 4, 5]
  const interactive = Boolean(onChange)

  return (
    <div className="flex items-center gap-1" role={interactive ? 'radiogroup' : undefined}>
      {stars.map((star) => {
        const filled = star <= Math.round(value)
        return (
          <button
            key={star}
            type="button"
            aria-label={`${star} star${star > 1 ? 's' : ''}`}
            aria-pressed={filled}
            disabled={!interactive}
            onClick={() => onChange?.(star)}
            className={interactive ? 'cursor-pointer' : 'cursor-default'}
          >
            <StarIcon
              style={{ width: size, height: size }}
              className={filled ? 'text-star' : 'text-border'}
            />
          </button>
        )
      })}
    </div>
  )
}

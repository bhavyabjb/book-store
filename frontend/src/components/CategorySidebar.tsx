import type { Category } from '@/types'

interface CategorySidebarProps {
  categories: Category[]
  selected: string | null
  onSelect: (slug: string | null) => void
}

export function CategorySidebar({ categories, selected, onSelect }: CategorySidebarProps) {
  return (
    <aside className="w-56 shrink-0" aria-label="Categories">
      <ul className="flex flex-col gap-1 text-sm">
        <li>
          <button
            type="button"
            onClick={() => onSelect(null)}
            className={`w-full rounded-md px-3 py-2 text-left ${
              selected === null ? 'bg-surface-2 font-semibold text-text' : 'text-text-muted hover:text-text'
            }`}
          >
            All
          </button>
        </li>
        {categories.map((category) => (
          <li key={category.id}>
            <button
              type="button"
              onClick={() => onSelect(category.slug)}
              className={`w-full rounded-md px-3 py-2 text-left ${
                selected === category.slug
                  ? 'bg-surface-2 font-semibold text-text'
                  : 'text-text-muted hover:text-text'
              }`}
            >
              {category.name}
            </button>
          </li>
        ))}
      </ul>
    </aside>
  )
}

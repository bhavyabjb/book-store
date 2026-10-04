import type { Category } from '@/types'

/** Walks parentId links to build a root -> leaf chain of category names. */
export function buildCategoryChain(categories: Category[], categoryId: number): Category[] {
  const byId = new Map(categories.map((c) => [c.id, c]))
  const chain: Category[] = []
  let current = byId.get(categoryId)
  const seen = new Set<number>()
  while (current && !seen.has(current.id)) {
    chain.unshift(current)
    seen.add(current.id)
    current = current.parentId !== null && current.parentId !== undefined ? byId.get(current.parentId) : undefined
  }
  return chain
}

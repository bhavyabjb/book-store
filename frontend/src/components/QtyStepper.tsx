interface QtyStepperProps {
  quantity: number
  onIncrement: () => void
  onDecrement: () => void
  disabled?: boolean
}

export function QtyStepper({ quantity, onIncrement, onDecrement, disabled }: QtyStepperProps) {
  return (
    <div className="flex items-center gap-3 border-b border-border pb-2 text-sm">
      <span data-testid="qty-value">{quantity}</span>
      <button
        type="button"
        aria-label="Decrease quantity"
        disabled={disabled}
        onClick={onDecrement}
        className="text-text-muted hover:text-text disabled:opacity-40"
      >
        &minus;
      </button>
      <span className="h-4 w-px bg-border" />
      <button
        type="button"
        aria-label="Increase quantity"
        disabled={disabled}
        onClick={onIncrement}
        className="text-text-muted hover:text-text disabled:opacity-40"
      >
        +
      </button>
    </div>
  )
}

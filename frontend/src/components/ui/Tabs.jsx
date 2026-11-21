// Selector segmentado (MENSUAL / SEMANAL / ANUAL, Todos / Gastos / Ingresos)
export default function Tabs({ options, value, onChange, className = '' }) {
  return (
    <div
      role="tablist"
      className={`inline-flex rounded-xl border border-line bg-app p-1 ${className}`}
    >
      {options.map((opt) => {
        const active = opt.value === value
        return (
          <button
            key={opt.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange?.(opt.value)}
            className={`rounded-lg px-4 py-1.5 text-[11px] font-semibold uppercase transition ${
              active ? 'bg-surface text-primary shadow-sm' : 'text-muted hover:text-ink'
            }`}
          >
            {opt.label}
          </button>
        )
      })}
    </div>
  )
}

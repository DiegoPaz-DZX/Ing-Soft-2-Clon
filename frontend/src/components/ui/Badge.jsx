const TONES = {
  neutral: 'bg-app text-muted border-line',
  primary: 'bg-primary-soft text-primary border-primary-soft',
  income: 'bg-income-soft text-income border-income-soft',
  expense: 'bg-expense-soft text-expense border-expense-soft',
  warning: 'bg-warning-soft text-warning border-warning-soft',
}

export default function Badge({ tone = 'neutral', className = '', children }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-md border px-2 py-0.5 text-[10px] font-semibold uppercase ${TONES[tone]} ${className}`}
    >
      {children}
    </span>
  )
}

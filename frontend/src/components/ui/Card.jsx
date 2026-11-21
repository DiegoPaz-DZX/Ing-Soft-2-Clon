const TONES = {
  default: 'bg-surface border-line',
  primary: 'bg-primary-soft border-primary-soft',
  mint: 'bg-linear-to-r from-mint to-income-soft border-mint',
  income: 'bg-income-soft/60 border-income-soft',
  expense: 'bg-expense-soft/60 border-expense-soft',
}

export default function Card({ tone = 'default', className = '', children, ...props }) {
  return (
    <div
      className={`rounded-card border p-5 shadow-card ${TONES[tone]} ${className}`}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardTitle({ children, className = '' }) {
  return <h3 className={`label-caps mb-3 ${className}`}>{children}</h3>
}

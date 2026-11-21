import { useId } from 'react'

export default function Input({ label, icon: Icon, className = '', id, ...props }) {
  const autoId = useId()
  const inputId = id ?? autoId

  return (
    <div className={className}>
      {label && (
        <label htmlFor={inputId} className="label-caps mb-1.5 block text-ink">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && (
          <Icon
            size={16}
            className="pointer-events-none absolute top-1/2 left-3 -translate-y-1/2 text-muted"
          />
        )}
        <input
          id={inputId}
          className={`w-full rounded-xl border border-line bg-app py-2.5 pr-3 text-sm text-ink placeholder:text-muted/70 focus:border-primary focus:bg-surface focus:ring-2 focus:ring-primary/20 focus:outline-none ${Icon ? 'pl-9' : 'pl-3'}`}
          {...props}
        />
      </div>
    </div>
  )
}

const VARIANTS = {
  // Botón principal con degradado morado → índigo (Guardar objetivo, Descargar PDF)
  primary:
    'bg-linear-to-r from-primary to-accent text-white shadow-sm hover:brightness-110',
  // Botón oscuro (Registrar transacción)
  dark: 'bg-navy text-white hover:bg-ink',
  // Botón morado sólido pequeño (+ Crear meta)
  solid: 'bg-primary text-white hover:bg-primary-dark',
  outline: 'border border-line bg-surface text-ink hover:bg-app',
  ghost: 'text-muted hover:text-ink',
}

const SIZES = {
  sm: 'px-3 py-1.5 text-[11px]',
  md: 'px-4 py-2.5 text-xs',
  lg: 'px-6 py-3 text-sm',
}

export default function Button({
  variant = 'primary',
  size = 'md',
  block = false,
  className = '',
  children,
  ...props
}) {
  return (
    <button
      type="button"
      className={`inline-flex items-center justify-center gap-2 rounded-xl font-semibold tracking-wide uppercase transition disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant]} ${SIZES[size]} ${block ? 'w-full' : ''} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

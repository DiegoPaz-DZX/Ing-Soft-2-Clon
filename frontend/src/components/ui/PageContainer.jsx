import { Link } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

// Contenedor blanco grande que envuelve cada pantalla en los mockups
export default function PageContainer({ title, subtitle, backTo, actions, children }) {
  return (
    <section className="rounded-card border border-line bg-surface p-5 shadow-card sm:p-8">
      <header className="mb-6 flex flex-wrap items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          {backTo && (
            <Link
              to={backTo}
              className="mt-1 rounded-full p-1 text-ink hover:bg-app"
              aria-label="Volver"
            >
              <ArrowLeft size={18} />
            </Link>
          )}
          <div>
            <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
            {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
          </div>
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </header>
      {children}
    </section>
  )
}

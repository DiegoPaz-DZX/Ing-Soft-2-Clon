import { X } from 'lucide-react'
import { Badge } from './ui'

// Cada nivel que devuelve el backend se traduce a un color y un texto
const NIVELES = {
  advertencia: { tone: 'warning', texto: 'Atención' },
  informacion: { tone: 'primary', texto: 'Información' },
  positivo: { tone: 'income', texto: 'Buen trabajo' },
}

export default function RecomendacionCard({ recomendacion, onDescartar }) {
  const nivel = NIVELES[recomendacion.nivel] ?? NIVELES.informacion

  return (
    <article className="relative rounded-2xl border border-line bg-app/60 p-4">
      <button
        type="button"
        onClick={() => onDescartar(recomendacion.id)}
        aria-label="Descartar recomendación"
        className="absolute top-3 right-3 rounded-full p-1 text-muted hover:bg-surface hover:text-ink"
      >
        <X size={14} />
      </button>

      <div className="mb-2 flex items-center gap-2 pr-6">
        <Badge tone={nivel.tone}>{nivel.texto}</Badge>
        {recomendacion.dato && (
          <span className="text-xs font-bold text-ink">{recomendacion.dato}</span>
        )}
      </div>

      <h4 className="text-sm font-semibold">{recomendacion.titulo}</h4>
      <p className="mt-1 text-xs leading-relaxed text-muted">{recomendacion.mensaje}</p>
    </article>
  )
}
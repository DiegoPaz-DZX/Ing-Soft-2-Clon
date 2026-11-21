import { useEffect, useState } from 'react'
import { obtenerTips } from '../services/api.js'

export default function TipsEducativos() {
  const [tips, setTips] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    obtenerTips()
      .then(setTips)
      .catch(() => setError(true))
      .finally(() => setCargando(false))
  }, [])

  if (cargando) {
    return <p className="text-sm text-muted">Cargando tips...</p>
  }

  if (error) {
    return (
      <p className="rounded-2xl bg-expense-soft/60 p-4 text-sm text-expense">
        No se pudieron cargar los tips. Verifica que el backend esté encendido.
      </p>
    )
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {tips.map((tip) => (
        <article key={tip.numero} className="flex gap-3 rounded-2xl border border-line bg-app/60 p-4">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-white">
            {tip.numero}
          </span>
          <div>
            <h4 className="text-sm font-semibold">{tip.titulo}</h4>
            <p className="mt-1 text-xs leading-relaxed text-muted">{tip.contenido}</p>
          </div>
        </article>
      ))}
    </div>
  )
}

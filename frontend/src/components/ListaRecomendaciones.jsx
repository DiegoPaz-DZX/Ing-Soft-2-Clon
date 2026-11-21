import { useEffect, useState } from 'react'
import { obtenerRecomendaciones } from '../services/api.js'
import RecomendacionCard from './RecomendacionCard.jsx'

export default function ListaRecomendaciones() {
  const [recomendaciones, setRecomendaciones] = useState([])
  const [descartadas, setDescartadas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    obtenerRecomendaciones()
      .then(setRecomendaciones)
      .catch(() => setError(true))
      .finally(() => setCargando(false))
  }, [])

  const descartar = (id) => setDescartadas((actuales) => [...actuales, id])
  const visibles = recomendaciones.filter((r) => !descartadas.includes(r.id))

  if (cargando) {
    return <p className="text-sm text-muted">Analizando tus gastos...</p>
  }

  if (error) {
    return (
      <p className="rounded-2xl bg-expense-soft/60 p-4 text-sm text-expense">
        No se pudieron cargar las recomendaciones. Verifica que el backend esté encendido.
      </p>
    )
  }

  if (recomendaciones.length === 0) {
    return (
      <p className="text-sm text-muted">
        Aún no hay suficientes movimientos para recomendarte algo. Registra más ingresos y
        gastos para ver recomendaciones personalizadas.
      </p>
    )
  }

  if (visibles.length === 0) {
    return <p className="text-sm text-muted">Descartaste todas las recomendaciones por ahora.</p>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      {visibles.map((r) => (
        <RecomendacionCard key={r.id} recomendacion={r} onDescartar={descartar} />
      ))}
    </div>
  )
}
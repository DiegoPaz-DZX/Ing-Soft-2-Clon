import { useEffect, useState } from 'react'
import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { obtenerUsuario } from '../services/sesion.js'

const URL_PROYECCION = 'http://localhost:8000/api/proyeccion'
const INTERVALO_MS = 5000

function formatear(valor) {
  return 'S/ ' + Number(valor).toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

export default function MonitorProyeccion() {
  const [proyeccion, setProyeccion] = useState(null)
  const [error, setError] = useState(false)

  useEffect(() => {
    let activo = true

    function cargar() {
      const usuario = obtenerUsuario()
      fetch(URL_PROYECCION, { headers: { Authorization: usuario?.token ? `Bearer ${usuario.token}` : '' } })
        .then((respuesta) => {
          if (!respuesta.ok) throw new Error('No se pudo obtener la proyección')
          return respuesta.json()
        })
        .then((datos) => {
          if (!activo) return
          setProyeccion(datos)
          setError(false)
        })
        .catch(() => {
          if (activo) setError(true)
        })
    }

    cargar()
    const temporizador = setInterval(cargar, INTERVALO_MS)
    return () => {
      activo = false
      clearInterval(temporizador)
    }
  }, [])

  if (error && !proyeccion) {
    return (
      <p className="rounded-2xl bg-expense-soft/60 p-4 text-sm text-expense">
        No se pudo conectar con el servidor. Verifica que el backend esté encendido.
      </p>
    )
  }

  if (!proyeccion) {
    return <p className="text-sm text-muted">Calculando proyección...</p>
  }

  const hayAlerta = proyeccion.haySobregasto

  return (
    <div>
      <div
        className={`flex items-start gap-3 rounded-2xl p-4 ${
          hayAlerta ? 'bg-expense-soft/60' : 'bg-income-soft/60'
        }`}
      >
        {hayAlerta ? (
          <AlertTriangle className="shrink-0 text-expense" size={24} />
        ) : (
          <CheckCircle2 className="shrink-0 text-income" size={24} />
        )}
        <p className="text-sm">{proyeccion.sugerencia}</p>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-2xl bg-surface p-4">
          <p className="label-caps">Gastado este mes</p>
          <p className="text-lg font-semibold">{formatear(proyeccion.gastoActual)}</p>
        </div>
        <div className="rounded-2xl bg-surface p-4">
          <p className="label-caps">Proyección al cierre</p>
          <p className={`text-lg font-semibold ${hayAlerta ? 'text-expense' : 'text-income'}`}>
            {formatear(proyeccion.gastoProyectado)}
          </p>
        </div>
        <div className="rounded-2xl bg-surface p-4">
          <p className="label-caps">Ingresos del mes</p>
          <p className="text-lg font-semibold">{formatear(proyeccion.ingresosMes)}</p>
        </div>
      </div>

      {proyeccion.gastoAtipico > 0 && (
        <p className="mt-3 text-xs text-muted">
          Gasto único excluido de la tendencia: {formatear(proyeccion.gastoAtipico)}
        </p>
      )}
    </div>
  )
}
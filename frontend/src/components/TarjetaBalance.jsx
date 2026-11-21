import { useEffect, useState } from 'react'
import { ArrowDownCircle, ArrowUpCircle, RefreshCw } from 'lucide-react'
import { obtenerBalance } from '../services/api.js'
import { useMoneda } from '../context/MonedaContext.jsx'

const INTERVALO_MS = 5000

export default function TarjetaBalance() {
  const { divisa } = useMoneda()
  const [balance, setBalance] = useState(null)
  const [error, setError] = useState(false)
  const [actualizado, setActualizado] = useState(null)

  useEffect(() => {
    let activo = true

    function cargar() {
      obtenerBalance()
        .then((datos) => {
          if (!activo) return
          setBalance(datos)
          setError(false)
          setActualizado(new Date())
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

  if (error && !balance) {
    return (
      <p className="rounded-2xl bg-expense-soft/60 p-4 text-sm text-expense">
        No se pudo conectar con el servidor. Verifica que el backend esté encendido.
      </p>
    )
  }

  if (!balance) {
    return <p className="text-sm text-muted">Cargando balance...</p>
  }

  const tarjeta = balance[divisa.codigo] ?? balance
  const formatear = (monto) =>
    `${divisa.simbolo} ${Number(monto).toLocaleString('es-PE', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })}`
  const disponible = Number(tarjeta.balance)

  return (
    <div>
      <p className="text-xs text-muted">Disponible en {divisa.nombre.toLowerCase()}</p>
      <p
        className={`text-4xl font-bold tracking-tight ${
          disponible < 0 ? 'text-expense' : 'text-ink'
        }`}
      >
        {formatear(disponible * divisa.solesPorUnidad)}
      </p>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <div className="flex items-center gap-3 rounded-2xl bg-surface p-4">
          <ArrowUpCircle className="text-income" size={28} />
          <div>
            <p className="label-caps">Ingresos</p>
            <p className="text-lg font-semibold text-income">
              {formatear(tarjeta.totalIngresos)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3 rounded-2xl bg-surface p-4">
          <ArrowDownCircle className="text-expense" size={28} />
          <div>
            <p className="label-caps">Gastos</p>
            <p className="text-lg font-semibold text-expense">
              {formatear(tarjeta.totalGastos)}
            </p>
          </div>
        </div>
      </div>

      <p className="mt-4 flex items-center gap-1.5 text-[11px] text-muted">
        <RefreshCw size={12} className={error ? 'text-expense' : 'text-income'} />
        {error
          ? 'Sin conexión. Mostrando el último dato.'
          : 'Actualizado a las ' + actualizado.toLocaleTimeString('es-PE') + ' (se actualiza solo)'}
      </p>
    </div>
  )
}
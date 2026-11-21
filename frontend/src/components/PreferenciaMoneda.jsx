import { useState } from 'react'
import { Check } from 'lucide-react'
import { useMoneda } from '../context/MonedaContext.jsx'

function formatearFecha(iso) {
  const [anio, mes, dia] = iso.split('-')
  return `${dia}/${mes}/${anio}`
}

export default function PreferenciaMoneda() {
  const { divisa, opciones, tipoCambio, cargando, cambiarDivisa } = useMoneda()
  const [guardando, setGuardando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')

  async function elegir(codigo) {
    if (codigo === divisa.codigo || guardando) return
    setGuardando(true)
    setMensaje('')
    setError('')
    try {
      const nueva = await cambiarDivisa(codigo)
      setMensaje(`Tu divisa base ahora es ${nueva.nombre}.`)
    } catch (e) {
      setError(e.message)
    } finally {
      setGuardando(false)
    }
  }

  if (cargando) {
    return <p className="text-sm text-muted">Cargando preferencias...</p>
  }

  return (
    <div>
      <p className="mb-3 text-xs text-muted">
        Elige la divisa en la que quieres ver tus montos.
      </p>

      <div role="radiogroup" aria-label="Divisa base" className="grid gap-3 sm:grid-cols-2">
        {opciones.map((opcion) => {
          const activa = opcion.codigo === divisa.codigo
          return (
            <button
              key={opcion.codigo}
              type="button"
              role="radio"
              aria-checked={activa}
              disabled={guardando}
              onClick={() => elegir(opcion.codigo)}
              className={`flex items-center gap-3 rounded-2xl border p-4 text-left transition disabled:opacity-60 ${
                activa
                  ? 'border-primary bg-primary-soft'
                  : 'border-line bg-surface hover:border-primary/50'
              }`}
            >
              <span
                className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl text-sm font-bold ${
                  activa ? 'bg-primary text-white' : 'bg-app text-ink'
                }`}
              >
                {opcion.simbolo}
              </span>
              <span className="flex-1">
                <span className="block text-sm font-semibold">{opcion.nombre}</span>
                <span className="block text-[11px] text-muted">{opcion.codigo}</span>
              </span>
              {activa && <Check size={18} className="text-primary" />}
            </button>
          )
        })}
      </div>

      {tipoCambio && (
        <p className="mt-4 rounded-2xl bg-app p-4 text-xs text-muted">
          Tipo de cambio del {formatearFecha(tipoCambio.fecha)}:{' '}
          <span className="font-semibold text-ink">
            1 USD = S/ {tipoCambio.solesPorDolar.toFixed(4)}
          </span>
        </p>
      )}

      {mensaje && (
        <p role="status" className="mt-3 rounded-xl bg-income-soft px-3 py-2 text-xs text-income">
          {mensaje}
        </p>
      )}
      {error && (
        <p role="alert" className="mt-3 rounded-xl bg-expense-soft px-3 py-2 text-xs text-expense">
          {error}
        </p>
      )}
    </div>
  )
}

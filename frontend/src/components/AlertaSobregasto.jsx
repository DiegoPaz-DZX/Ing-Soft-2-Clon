import { AlertCircle, X } from 'lucide-react'
import { useState } from 'react'

export default function AlertaSobregasto({ alerta, onCerrar }) {
  const [mostrar, setMostrar] = useState(true)
  if (!mostrar) return null

  const esAlertaCritica = alerta.tipo_alerta === 'critica'
  const colorFondo = esAlertaCritica ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
  const colorTexto = esAlertaCritica ? 'text-red-800' : 'text-yellow-800'
  const colorIcono = esAlertaCritica ? 'text-red-500' : 'text-yellow-500'

  return (
    <div className={`rounded-lg border p-4 ${colorFondo}`} role="alert">
      <div className="flex items-start gap-3">
        <AlertCircle className={`mt-0.5 flex-shrink-0 ${colorIcono}`} size={20} />
        <div className="flex-1">
          <h3 className={`font-semibold ${colorTexto}`}>{esAlertaCritica ? '¡Alerta Crítica!' : 'Advertencia de Gasto'}</h3>
          <p className={`mt-1 text-sm ${colorTexto}`}>{alerta.descripcion}</p>
          <p className={`mt-2 text-xs font-mono ${colorTexto}`}>
            {alerta.categoria}: S/ {parseFloat(alerta.monto_gastado).toFixed(2)} de S/ {parseFloat(alerta.monto_limite).toFixed(2)} ({parseFloat(alerta.porcentaje_usado).toFixed(1)}%)
          </p>
        </div>
        <button onClick={() => { setMostrar(false); if (onCerrar) onCerrar() }} className={`flex-shrink-0 ${colorTexto}`}>
          <X size={20} />
        </button>
      </div>
    </div>
  )
}
import { useState } from 'react'
import { Modal } from '../ui'
import SelectorCategoria from './SelectorCategoria'
import { MONEDAS } from '../../domain/monedas'
import { useMoneda } from '../../context/MonedaContext.jsx'

const claseInput =
  'w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400'

export default function FormularioEdicionTransaccion({
  movimiento,
  categorias,
  guardando,
  error,
  onGuardar,
  onCancelar,
  metas = [],
}) {
  const { opciones: monedasDisponibles } = useMoneda()
  const monedas = monedasDisponibles?.length ? monedasDisponibles : MONEDAS
  const [tipo, setTipo] = useState(movimiento.tipo)
  const [monto, setMonto] = useState(String(movimiento.monto))
  const [fecha, setFecha] = useState(movimiento.fecha)
  const [descripcion, setDescripcion] = useState(movimiento.descripcion ?? '')
  const [categoria, setCategoria] = useState(movimiento.categoria ?? '')
  const [moneda, setMoneda] = useState(movimiento.moneda ?? 'PEN')
  const [metaId, setMetaId] = useState(movimiento.meta_id ? String(movimiento.meta_id) : '')
  const [errorLocal, setErrorLocal] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!(Number(monto) > 0)) return setErrorLocal('El monto debe ser mayor a 0')
    if (!fecha) return setErrorLocal('La fecha es obligatoria')
    if (tipo === 'GASTO' && !categoria) return setErrorLocal('Selecciona una categoría para el gasto')
    if (tipo === 'GASTO' && categoria === 'ahorro' && !metaId) {
      return setErrorLocal('Selecciona la meta que recibirá este ahorro')
    }
    setErrorLocal('')
    onGuardar({
      tipo,
      monto,
      fecha,
      descripcion: descripcion.trim(),
      categoria: tipo === 'GASTO' ? categoria : '',
      moneda,
      meta_id: tipo === 'GASTO' && categoria === 'ahorro' ? metaId : null,
    })
  }

  return (
    <Modal
      open
      onClose={guardando ? undefined : onCancelar}
      title="Editar transacción"
      subtitle="Corrige los datos del movimiento."
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        <label className="block text-sm">
          Tipo
          <select value={tipo} onChange={(e) => setTipo(e.target.value)} className={claseInput}>
            <option value="GASTO">Gasto</option>
            <option value="INGRESO">Ingreso</option>
          </select>
        </label>

        {tipo === 'GASTO' && categoria === 'ahorro' && (
          <label className="block text-sm">
            Meta de ahorro
            <select value={metaId} onChange={(e) => setMetaId(e.target.value)} className={claseInput}>
              <option value="">Selecciona la meta</option>
              {metas.map((meta) => <option key={meta.id} value={meta.id}>{meta.nombre}</option>)}
            </select>
          </label>
        )}

        <label className="block text-sm">
          Monto
          <input
            type="number"
            step="0.01"
            min="0"
            value={monto}
            onChange={(e) => setMonto(e.target.value)}
            className={claseInput}
          />
        </label>

        <label className="block text-sm">
          Fecha
          <input
            type="date"
            value={fecha}
            onChange={(e) => setFecha(e.target.value)}
            className={claseInput}
          />
        </label>

        <label className="block text-sm">
          Descripción
          <input
            type="text"
            value={descripcion}
            onChange={(e) => setDescripcion(e.target.value)}
            className={claseInput}
          />
        </label>

        {tipo === 'GASTO' && (
          <SelectorCategoria value={categoria} onChange={setCategoria} categorias={categorias} />
        )}

        <label className="block text-sm">
          Moneda
          <select value={moneda} onChange={(e) => setMoneda(e.target.value)} className={claseInput}>
            {monedas.map((m) => (
              <option key={m.codigo} value={m.codigo}>
                {m.nombre}
              </option>
            ))}
          </select>
        </label>

        {(errorLocal || error) && (
          <p role="alert" className="text-sm text-red-600">
            {errorLocal || error}
          </p>
        )}

        <div className="flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancelar}
            disabled={guardando}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={guardando}
            className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:opacity-50"
          >
            {guardando ? 'Guardando…' : 'Guardar cambios'}
          </button>
        </div>
      </form>
    </Modal>
  )
}

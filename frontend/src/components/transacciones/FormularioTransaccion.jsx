import { useState } from 'react'
import { Button, Input } from '../ui'
import { Transaccion, TipoTransaccion } from '../../domain/Transaccion'
import SelectorComprobante from './SelectorComprobante' // NUEVO

const hoy = () => new Date().toLocaleDateString('en-CA') // AAAA-MM-DD

const claseSelect =
  'w-full rounded-xl border border-line bg-app px-3 py-2.5 text-sm text-ink focus:border-primary focus:bg-surface focus:ring-2 focus:ring-primary/20 focus:outline-none'

export default function FormularioTransaccion({ onRegistrar }) {
  const [tipo, setTipo] = useState(TipoTransaccion.GASTO)
  const [moneda, setMoneda] = useState('PEN')
  const [monto, setMonto] = useState('')
  const [fecha, setFecha] = useState(hoy())
  const [comprobante, setComprobante] = useState(null) // NUEVO
  const [error, setError] = useState('')
  const [guardado, setGuardado] = useState(false)

  const handleSubmit = (e) => {
    e.preventDefault()
    setGuardado(false)

    try {
      // La clase Transaccion valida sus propios datos
      // NUEVO: 'PEN' es la moneda, undefined deja el id automático, y al final va el comprobante
      const transaccion = new Transaccion(tipo, monto, fecha, moneda, undefined, comprobante)
      onRegistrar(transaccion)
      setMonto('')
      setComprobante(null) // NUEVO: limpiar el archivo después de guardar
      setError('')
      setGuardado(true)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-4">
      <div>
        <label htmlFor="tipo-transaccion" className="label-caps mb-1.5 block text-ink">
          Tipo
        </label>
        <select
          id="tipo-transaccion"
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
          className={claseSelect}
        >
          <option value={TipoTransaccion.GASTO}>Gasto</option>
          <option value={TipoTransaccion.INGRESO}>Ingreso</option>
        </select>
      </div>

      <Input
        label="Monto"
        type="number"
        step="0.01"
        min="0"
        placeholder="0.00"
        value={monto}
        onChange={(e) => setMonto(e.target.value)}
      />

      <select value={moneda} onChange={(e) => setMoneda(e.target.value)} className={claseSelect}>
        <option value="PEN">Soles (S/.)</option>
        <option value="USD">Dólares ($)</option>
      </select>

      <Input
        label="Fecha"
        type="date"
        value={fecha}
        onChange={(e) => setFecha(e.target.value)}
      />

      {/* NUEVO: selector del comprobante, debajo de la fecha */}
      <SelectorComprobante archivo={comprobante} onChange={setComprobante} />

      {error && (
        <p role="alert" className="rounded-xl bg-expense-soft px-3 py-2 text-xs text-expense">
          {error}
        </p>
      )}
      {guardado && (
        <p role="status" className="rounded-xl bg-income-soft px-3 py-2 text-xs text-income">
          Transacción registrada.
        </p>
      )}

      <Button type="submit" variant="dark" block>
        Registrar
      </Button>
    </form>
  )
}
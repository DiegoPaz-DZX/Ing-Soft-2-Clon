import { useState } from 'react'
import { Button } from '../ui'

export default function FormularioAbono({ simbolo, onAbonar }) {
  const [monto, setMonto] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      await onAbonar(monto)
      setMonto('')
      setError('')
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 grid gap-2">
      <input
        type="number"
        min="0"
        step="0.01"
        placeholder={`Monto a abonar (${simbolo})`}
        aria-label="Monto a abonar"
        className="w-full rounded-md border border-gray-300 p-2"
        value={monto}
        onChange={(e) => setMonto(e.target.value)}
      />
      {error && (
        <p role="alert" className="text-sm text-red-600">
          {error}
        </p>
      )}
      <Button type="submit" size="lg" block>
        Abonar a la meta
      </Button>
    </form>
  )
}

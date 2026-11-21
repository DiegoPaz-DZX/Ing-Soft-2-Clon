import { useState } from 'react'
import { Button, Card, CardTitle } from './ui'
import { useMoneda } from '../context/MonedaContext.jsx'
import { descargarReporteMensual } from '../services/ServicioExportacion.js'

export default function ExportarConDivisa() {
  const { divisa } = useMoneda()
  const [fecha, setFecha] = useState('')
  const [formato, setFormato] = useState('pdf')
  const [exportando, setExportando] = useState(false)
  const [error, setError] = useState('')

  async function exportar(event) {
    event.preventDefault()
    if (!fecha) return setError('Por favor, selecciona un mes para exportar el reporte.')
    const [anio, mes] = fecha.split('-')
    setError('')
    setExportando(true)
    try {
      await descargarReporteMensual({ anio, mes, formato })
    } catch (e) {
      setError(e.message)
    } finally {
      setExportando(false)
    }
  }

  return (
    <Card>
      <CardTitle>Exportar con la divisa del perfil</CardTitle>
      <form onSubmit={exportar}>
        <input
          className="rounded border border-line px-3 py-2"
          type="month"
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
        />
        <select
          className="mt-3 block w-full rounded border border-line px-3 py-2"
          value={formato}
          onChange={(e) => setFormato(e.target.value)}
        >
          <option value="pdf">PDF</option>
          <option value="excel">Excel</option>
        </select>
        <p className="mt-3 text-sm text-muted">
          El reporte se exportará en {divisa.nombre} ({divisa.codigo}), la moneda de
          visualización de tu perfil.
        </p>
        {error && (
          <p className="mt-2 text-sm text-red-600" role="alert">
            {error}
          </p>
        )}
        <Button type="submit" size="lg" block disabled={exportando} className="mt-6">
          {exportando ? 'Generando...' : 'Exportar con mi divisa'}
        </Button>
      </form>
    </Card>
  )
}
import { useState } from 'react'
import { FileSpreadsheet, Upload } from 'lucide-react'
import { importarMovimientos } from '../../services/api.js'

const EXTENSIONES = ['csv', 'xls', 'xlsx']

export default function ImportadorMovimientos({ onImportado }) {
  const [archivo, setArchivo] = useState(null)
  const [cargando, setCargando] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [error, setError] = useState('')
  const [detalles, setDetalles] = useState([])

  const seleccionarArchivo = (e) => {
    setArchivo(e.target.files?.[0] ?? null)
    setMensaje('')
    setError('')
    setDetalles([])
  }

  const importar = async (e) => {
    e.preventDefault()
    const formulario = e.currentTarget
    setMensaje('')
    setError('')
    setDetalles([])

    if (!archivo) {
      setError('Selecciona un archivo primero.')
      return
    }

    const extension = archivo.name.split('.').pop()?.toLowerCase()
    if (!EXTENSIONES.includes(extension)) {
      setError('El archivo debe ser CSV, XLS o XLSX.')
      return
    }

    setCargando(true)
    try {
      const respuesta = await importarMovimientos(archivo)
      setMensaje(`${respuesta.importados} movimientos importados.`)
      setArchivo(null)
      formulario.reset()
      await onImportado?.()
    } catch (err) {
      setError(err.message)
      setDetalles(err.detalles ?? [])
    } finally {
      setCargando(false)
    }
  }

  return (
    <form onSubmit={importar} className="mt-4 space-y-4">
      <div className="rounded-xl border border-dashed border-gray-300 bg-gray-50 p-5 text-center">
        <FileSpreadsheet className="mx-auto text-gray-500" size={32} />
        <p className="mt-2 text-sm font-medium">Sube tu archivo CSV o Excel</p>
        <p className="mt-1 text-xs text-gray-500">Máximo 500 movimientos y 5 MB.</p>
        <label className="mt-4 inline-flex cursor-pointer items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm hover:bg-gray-100">
          <Upload size={16} />
          Elegir archivo
          <input
            type="file"
            accept=".csv,.xls,.xlsx"
            onChange={seleccionarArchivo}
            className="sr-only"
          />
        </label>
        {archivo && <p className="mt-3 break-all text-xs text-gray-600">{archivo.name}</p>}
      </div>

      <p className="text-xs leading-5 text-gray-500">
        Usa las columnas <strong>tipo, monto y fecha</strong>. También puedes incluir descripción,
        categoría y moneda. La fecha va como AAAA-MM-DD.{' '}
        <a href="/plantilla_movimientos.csv" download className="font-medium text-primary hover:underline">
          Descargar ejemplo
        </a>
      </p>

      {mensaje && <p role="status" className="text-sm text-green-600">{mensaje}</p>}
      {error && <p role="alert" className="text-sm text-red-600">{error}</p>}
      {detalles.length > 0 && (
        <ul className="max-h-28 list-disc overflow-auto pl-5 text-xs text-red-600">
          {detalles.map((detalle) => (
            <li key={`${detalle.fila}-${detalle.error}`}>
              Fila {detalle.fila}: {detalle.error}
            </li>
          ))}
        </ul>
      )}

      <button
        type="submit"
        disabled={cargando}
        className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {cargando ? 'Importando...' : 'Importar movimientos'}
      </button>
    </form>
  )
}

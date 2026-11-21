import { useEffect, useRef, useState } from 'react'
import { FileText, Paperclip, X } from 'lucide-react'
import { Button } from '../ui'
import { COMPROBANTE_TIPOS, validarComprobante } from '../../domain/Transaccion'

export default function SelectorComprobante({ archivo, onChange }) {
  const inputRef = useRef(null)
  const [error, setError] = useState('')
  const [vistaPrevia, setVistaPrevia] = useState(null)

  // Miniatura solo para imágenes; libera la memoria al cambiar de archivo
  useEffect(() => {
    if (!archivo?.type.startsWith('image/')) {
      setVistaPrevia(null)
      return
    }
    const url = URL.createObjectURL(archivo)
    setVistaPrevia(url)
    return () => URL.revokeObjectURL(url)
  }, [archivo])

  // Si el formulario limpia el archivo (después de guardar), limpia también el input
  useEffect(() => {
    if (!archivo && inputRef.current) inputRef.current.value = ''
  }, [archivo])

  const handleChange = (e) => {
    const nuevo = e.target.files[0]
    if (!nuevo) return

    try {
      validarComprobante(nuevo)
      setError('')
      onChange(nuevo)
    } catch (err) {
      setError(err.message)
      e.target.value = ''
    }
  }

  const quitar = () => {
    setError('')
    onChange(null)
  }

  return (
    <div>
      <span className="label-caps mb-1.5 block text-ink">Comprobante (opcional)</span>

      <input
        ref={inputRef}
        id="comprobante"
        type="file"
        accept={COMPROBANTE_TIPOS.join(',')}
        onChange={handleChange}
        className="hidden"
      />

      {!archivo && (
        <Button variant="outline" block onClick={() => inputRef.current?.click()}>
          <Paperclip size={14} /> Adjuntar foto o PDF
        </Button>
      )}

      {archivo && (
        <div className="flex items-center gap-3 rounded-xl border border-line bg-app p-2">
          {vistaPrevia ? (
            <img src={vistaPrevia} alt="Vista previa del comprobante" className="h-12 w-12 rounded-lg object-cover" />
          ) : (
            <FileText size={32} className="text-primary" />
          )}
          <span className="min-w-0 flex-1 truncate text-xs text-ink">{archivo.name}</span>
          <button type="button" onClick={quitar} aria-label="Quitar comprobante" className="rounded-full p-1 text-ink hover:bg-surface">
            <X size={16} />
          </button>
        </div>
      )}

      {error && (
        <p role="alert" className="mt-2 rounded-xl bg-expense-soft px-3 py-2 text-xs text-expense">
          {error}
        </p>
      )}
    </div>
  )
}
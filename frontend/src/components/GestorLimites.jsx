import { useState, useEffect } from 'react'
import { Card, CardTitle, Button, Input } from './ui'
import { ServicioAlertas } from '../services/ServicioAlertas'
import { CATEGORIAS } from '../domain/categorias'

export default function GestorLimites() {
  const [limites, setLimites] = useState({})
  const [nuevaCategoria, setNuevaCategoria] = useState('')
  const [nuevoLimite, setNuevoLimite] = useState('')
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    (async () => {
      setCargando(true)
      const limitesObtenidos = await ServicioAlertas.obtenerLimites()
      setLimites(limitesObtenidos)
      setCargando(false)
    })()
  }, [])

  const handleAñadirLimite = async (e) => {
    e.preventDefault()
    if (!nuevaCategoria || !nuevoLimite) {
      setError('Completa todos los campos')
      return
    }
    try {
      await ServicioAlertas.establecerLimite(nuevaCategoria, parseFloat(nuevoLimite))
      setLimites({ ...limites, [nuevaCategoria]: parseFloat(nuevoLimite) })
      setNuevaCategoria('')
      setNuevoLimite('')
      setError('')
    } catch {
      setError('Error al establecer el límite')
    }
  }

  if (cargando) return <p className="text-sm text-gray-500">Cargando límites...</p>

  return (
    <Card>
      <CardTitle>Gestionar Límites de Gasto</CardTitle>
      {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
      <form onSubmit={handleAñadirLimite} className="mt-4 space-y-4">
        <select value={nuevaCategoria} onChange={(e) => setNuevaCategoria(e.target.value)} className="w-full rounded-lg border px-3 py-2">
          <option value="">Selecciona categoría</option>
          {CATEGORIAS.map((cat) => <option key={cat.id} value={cat.id}>{cat.nombre}</option>)}
        </select>
        <Input type="number" step="0.01" min="0" value={nuevoLimite} onChange={(e) => setNuevoLimite(e.target.value)} placeholder="0.00" />
        <Button type="submit" className="w-full">Establecer Límite</Button>
      </form>
      <div className="mt-6">
        <h4 className="font-semibold text-sm">Límites Actuales</h4>
        {Object.keys(limites).length === 0 ? (
          <p className="mt-2 text-sm text-gray-500">No hay límites</p>
        ) : (
          <ul className="mt-2 space-y-2">
            {Object.entries(limites).map(([categoria, limite]) => (
              <li key={categoria} className="flex justify-between bg-gray-50 p-3 rounded text-sm">
                <span>{categoria}</span>
                <span>S/ {Number(limite).toFixed(2)}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </Card>
  )
}

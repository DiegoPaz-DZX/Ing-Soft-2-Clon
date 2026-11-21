import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CalendarDays, Paperclip, Plus, Trash2, X } from 'lucide-react'
import { Badge, Button, Input, PageContainer } from '../components/ui'
import VisorComprobante from '../components/transacciones/VisorComprobante'
import ModalEliminar from '../components/transacciones/ModalEliminar'
import { useTransacciones } from '../context/TransaccionesContext'
import { useMoneda } from '../context/MonedaContext.jsx'
import { PATHS } from '../routes/paths.js'
import { eliminarMovimiento, obtenerMovimientos } from '../services/api.js'

function formatearFecha(iso) {
  const [a, m, d] = iso.split('-')
  return `${Number(d)}/${Number(m)}/${a}`
}

export default function Historial() {
  const { formatearMovimiento } = useMoneda()
  const { quitarPorBackendId } = useTransacciones()
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [movimientos, setMovimientos] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [filtroActivo, setFiltroActivo] = useState(false)
  const [comprobanteAbierto, setComprobanteAbierto] = useState(null)
  const [porEliminar, setPorEliminar] = useState(null)
  const [eliminando, setEliminando] = useState(false)
  const [errorEliminar, setErrorEliminar] = useState('')

  async function cargar(rango) {
    setCargando(true)
    setError('')
    try {
      setMovimientos(await obtenerMovimientos(rango))
      setFiltroActivo(Boolean(rango))
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    cargar()
  }, [])

  function filtrar(e) {
    e.preventDefault()
    cargar({ desde, hasta })
  }

  function limpiar() {
    setDesde('')
    setHasta('')
    cargar()
  }

  function pedirEliminar(movimiento) {
    setErrorEliminar('')
    setPorEliminar(movimiento)
  }

  function cancelarEliminar() {
    setPorEliminar(null)
    setErrorEliminar('')
  }

  async function confirmarEliminar() {
    setEliminando(true)
    setErrorEliminar('')
    try {
      await eliminarMovimiento(porEliminar.id)
      setMovimientos((actuales) => actuales.filter((m) => m.id !== porEliminar.id))
      quitarPorBackendId(porEliminar.id)
      setPorEliminar(null)
    } catch (e) {
      setErrorEliminar(e.message)
    } finally {
      setEliminando(false)
    }
  }

  return (
    <PageContainer
      title="Historial de Movimientos"
      subtitle="Audita el flujo de caja: egresos e ingresos de tus cuentas."
      actions={
        <Link to={PATHS.transacciones}>
          <Button variant="dark">
            <Plus size={14} /> Registrar transacción
          </Button>
        </Link>
      }
    >
      <form
        onSubmit={filtrar}
        className="mb-5 flex flex-wrap items-end gap-3 rounded-2xl border border-line bg-app/60 p-4"
      >
        <Input
          label="Desde"
          type="date"
          icon={CalendarDays}
          value={desde}
          onChange={(e) => setDesde(e.target.value)}
          className="min-w-40 flex-1"
        />
        <Input
          label="Hasta"
          type="date"
          icon={CalendarDays}
          value={hasta}
          onChange={(e) => setHasta(e.target.value)}
          className="min-w-40 flex-1"
        />
        <div className="flex gap-2">
          <Button type="submit" variant="solid" disabled={cargando}>
            Filtrar
          </Button>
          {filtroActivo && (
            <Button variant="outline" onClick={limpiar} disabled={cargando}>
              <X size={14} /> Limpiar
            </Button>
          )}
        </div>
      </form>

      {error && (
        <p className="mb-4 rounded-xl border border-expense-soft bg-expense-soft/60 px-4 py-2.5 text-sm text-expense">
          {error}
        </p>
      )}

      <div className="overflow-x-auto">
        <table className="w-full min-w-160 text-sm">
          <thead>
            <tr className="label-caps border-b border-line text-left">
              <th className="px-2 pb-2 font-semibold">Descripción</th>
              <th className="px-2 pb-2 font-semibold">Tipo</th>
              <th className="px-2 pb-2 font-semibold">Fecha</th>
              <th className="px-2 pb-2 font-semibold">Comprobante</th>
              <th className="px-2 pb-2 text-right font-semibold">Monto</th>
              <th className="px-2 pb-2 text-right font-semibold">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {movimientos.map((m) => {
              const ingreso = m.tipo === 'INGRESO'
              return (
                <tr key={m.id} className="border-b border-line/70 last:border-0">
                  <td className="px-2 py-3 font-medium">{m.descripcion}</td>
                  <td className="px-2 py-3">
                    <Badge tone={ingreso ? 'income' : 'expense'}>{ingreso ? 'Ingreso' : 'Gasto'}</Badge>
                  </td>
                  <td className="px-2 py-3 text-muted">{formatearFecha(m.fecha)}</td>
                  <td className="px-2 py-3">
                    {m.comprobante ? (
                      <button
                        type="button"
                        onClick={() => setComprobanteAbierto(m.comprobante)}
                        aria-label="Ver comprobante"
                      >
                        <Badge tone="primary" className="cursor-pointer hover:brightness-95">
                          <Paperclip size={10} /> Comprobante
                        </Badge>
                      </button>
                    ) : (
                      <span className="text-muted">—</span>
                    )}
                  </td>
                  <td
                    className={`px-2 py-3 text-right font-semibold tabular-nums ${ingreso ? 'text-income' : 'text-ink'}`}
                  >
                    {ingreso ? '+' : '-'} {formatearMovimiento(m.monto, m.moneda)}
                  </td>
                  <td className="px-2 py-3 text-right">
                    <button
                      type="button"
                      onClick={() => pedirEliminar(m)}
                      aria-label="Eliminar transacción"
                      className="rounded-full p-1.5 text-muted hover:bg-expense-soft hover:text-expense"
                    >
                      <Trash2 size={16} />
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>

      {!cargando && !error && movimientos.length === 0 && (
        <p className="py-10 text-center text-sm text-muted">
          No hay movimientos en el rango seleccionado.
        </p>
      )}
      {cargando && <p className="py-10 text-center text-sm text-muted">Cargando movimientos…</p>}

      <VisorComprobante
        comprobante={comprobanteAbierto}
        onClose={() => setComprobanteAbierto(null)}
      />

      <ModalEliminar
        open={Boolean(porEliminar)}
        detalle={
          porEliminar
            ? `${formatearFecha(porEliminar.fecha)} · ${porEliminar.tipo === 'INGRESO' ? 'Ingreso' : 'Gasto'} · ${porEliminar.descripcion || 'Sin descripción'} · ${formatearMovimiento(porEliminar.monto, porEliminar.moneda)}`
            : ''
        }
        eliminando={eliminando}
        error={errorEliminar}
        onConfirmar={confirmarEliminar}
        onCancelar={cancelarEliminar}
      />
    </PageContainer>
  )
}
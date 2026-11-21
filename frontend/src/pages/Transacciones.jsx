import { useEffect, useState } from 'react'
import { Pencil, Trash2 } from 'lucide-react'
import { Card, CardTitle, PageContainer } from '../components/ui'
import ImportadorMovimientos from '../components/transacciones/ImportadorMovimientos'
import SelectorCategoria from '../components/transacciones/SelectorCategoria'
import SelectorComprobante from '../components/transacciones/SelectorComprobante'
import ModalEliminar from '../components/transacciones/ModalEliminar'
import FormularioEdicionTransaccion from '../components/transacciones/FormularioEdicionTransaccion'
import { useTransacciones } from '../context/TransaccionesContext'
import { useMoneda } from '../context/MonedaContext.jsx'
import { sugerirCategoria } from '../services/ServicioSugerenciaCategoria'
import { buscarCategoria, CATEGORIAS } from '../domain/categorias'
import { formatearConMoneda, MONEDAS } from '../domain/monedas'
import {
  editarMovimiento,
  eliminarMovimiento,
  obtenerCategorias,
  obtenerMovimientos,
  obtenerMetas,
} from '../services/api.js'

const hoy = () => new Date().toLocaleDateString('en-CA') // AAAA-MM-DD

const claseInput =
  'w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-400'

export default function Transacciones() {
  const { registrarTransaccion, quitarPorBackendId, actualizarPorBackendId } = useTransacciones()
  const { divisa, opciones: monedasDisponibles } = useMoneda()
  const [tipo, setTipo] = useState('gasto')
  const [monto, setMonto] = useState('')
  const [moneda, setMoneda] = useState(divisa.codigo)
  const [fecha, setFecha] = useState(hoy())
  const [categoria, setCategoria] = useState('')
  const [categorias, setCategorias] = useState(CATEGORIAS)
  const [descripcion, setDescripcion] = useState('')
  const [categoriaSugerida, setCategoriaSugerida] = useState(null)
  const [metaId, setMetaId] = useState('')
  const [comprobante, setComprobante] = useState(null)
  const [error, setError] = useState('')
  const [movimientos, setMovimientos] = useState([])
  const [errorLista, setErrorLista] = useState('')
  const [porEliminar, setPorEliminar] = useState(null)
  const [eliminando, setEliminando] = useState(false)
  const [errorEliminar, setErrorEliminar] = useState('')
  const [editando, setEditando] = useState(null)
  const [guardandoEdicion, setGuardandoEdicion] = useState(false)
  const [errorEditar, setErrorEditar] = useState('')
  const [metas, setMetas] = useState([])
  const monedas = monedasDisponibles?.length ? monedasDisponibles : MONEDAS

  useEffect(() => {
    setMoneda(divisa.codigo)
  }, [divisa.codigo])

  const cargarMovimientos = () =>
    obtenerMovimientos()
      .then((datos) => {
        setMovimientos(datos)
        setErrorLista('')
      })
      .catch((e) => setErrorLista(e.message))

  useEffect(() => {
    cargarMovimientos()
  }, [])

  useEffect(() => {
    obtenerMetas().then((respuesta) => setMetas(respuesta.metas ?? [])).catch(() => setMetas([]))
  }, [])

  useEffect(() => {
    obtenerCategorias()
      .then((respuesta) => {
        const colores = Object.fromEntries(CATEGORIAS.map((item) => [item.id, item.color]))
        setCategorias(
          respuesta.map((item) => ({ ...item, color: colores[item.id] ?? 'bg-slate-500' })),
        )
      })
      .catch(() => setCategorias(CATEGORIAS))
  }, [])

  // HU15: sugiere la categoría al escribir, sin pisar una elección manual del usuario
  const cambiarDescripcion = (texto) => {
    setDescripcion(texto)
    const sugerida = sugerirCategoria(texto, categorias)
    const eligioManual = categoria !== '' && categoria !== categoriaSugerida
    if (eligioManual) return
    setCategoriaSugerida(sugerida)
    setCategoria(sugerida ?? '')
  }

  const elegirCategoria = (id) => {
    setCategoria(id)
    setCategoriaSugerida(null)
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    try {
      registrarTransaccion(
        tipo,
        monto,
        fecha,
        categoria,
        descripcion,
        comprobante,
        moneda,
        categoria === 'ahorro' ? metaId || null : null,
      )?.finally(cargarMovimientos)
      setMonto('')
      setDescripcion('')
      setCategoria('')
      setCategoriaSugerida(null)
      setMetaId('')
      setComprobante(null)
      setError('')
    } catch (err) {
      setError(err.message)
    }
  }

  const cancelarEliminar = () => {
    setPorEliminar(null)
    setErrorEliminar('')
  }

  const confirmarEliminar = async () => {
    setEliminando(true)
    setErrorEliminar('')
    try {
      await eliminarMovimiento(porEliminar.id)
      setMovimientos((actuales) => actuales.filter((m) => m.id !== porEliminar.id))
      quitarPorBackendId(porEliminar.id)
      setPorEliminar(null)
    } catch (err) {
      setErrorEliminar(err.message)
    } finally {
      setEliminando(false)
    }
  }

  const cancelarEdicion = () => {
    setEditando(null)
    setErrorEditar('')
  }

  const guardarEdicion = async (datos) => {
    setGuardandoEdicion(true)
    setErrorEditar('')
    try {
      const movimientoActualizado = await editarMovimiento(editando.id, datos)
      actualizarPorBackendId(editando.id, movimientoActualizado)
      await cargarMovimientos()
      setEditando(null)
    } catch (err) {
      setErrorEditar(err.message)
    } finally {
      setGuardandoEdicion(false)
    }
  }

  return (
    <PageContainer title="Transacciones" subtitle="Registra y organiza tus ingresos y gastos.">
      <div className="grid gap-5 md:grid-cols-2">
        <Card>
          <CardTitle>Nueva transacción</CardTitle>
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            <label className="block text-sm">
              Tipo
              <select value={tipo} onChange={(e) => setTipo(e.target.value)} className={claseInput}>
                <option value="gasto">Gasto</option>
                <option value="ingreso">Ingreso</option>
              </select>
            </label>

            <label className="block text-sm">
              Monto
              <input
                type="number"
                step="0.01"
                min="0"
                value={monto}
                onChange={(e) => setMonto(e.target.value)}
                placeholder={`0.00 (${divisa.codigo})`}
                className={claseInput}
              />
            </label>

            <label className="block text-sm">
              Descripción
              <input
                type="text"
                value={descripcion}
                onChange={(e) => cambiarDescripcion(e.target.value)}
                placeholder="Ej. almuerzo o pasaje"
                className={claseInput}
              />
            </label>

            {tipo === 'gasto' && (
              <>
                <SelectorCategoria
                  value={categoria}
                  onChange={elegirCategoria}
                  categorias={categorias}
                />
                {categoriaSugerida && categoria === categoriaSugerida && (
                  <p role="status" className="text-xs text-gray-500">
                    Categoría sugerida: {buscarCategoria(categoriaSugerida)?.nombre}. Puedes cambiarla.
                  </p>
                )}
                {categoria === 'ahorro' && (
                  <label className="block text-sm">
                    Meta de ahorro
                    <select
                      value={metaId}
                      onChange={(e) => setMetaId(e.target.value)}
                      className={claseInput}
                      required
                    >
                      <option value="">Selecciona la meta que recibirá este ahorro</option>
                      {metas.map((meta) => (
                        <option key={meta.id} value={meta.id}>{meta.nombre}</option>
                      ))}
                    </select>
                    {metas.length === 0 && (
                      <span className="mt-1 block text-xs text-amber-700">
                        Primero crea una meta para registrar un ahorro asignado.
                      </span>
                    )}
                    {metaId && (
                      <span role="status" className="mt-1 block text-xs text-green-700">
                        Este ahorro se sumará únicamente a: {metas.find((meta) => String(meta.id) === String(metaId))?.nombre}
                      </span>
                    )}
                  </label>
                )}
              </>
            )}

            <label className="block text-sm">
              Moneda
              <select
                value={moneda}
                onChange={(e) => setMoneda(e.target.value)}
                className={claseInput}
              >
                {monedas.map((m) => (
                  <option key={m.codigo} value={m.codigo}>
                    {m.nombre}
                  </option>
                ))}
              </select>
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

            <SelectorComprobante archivo={comprobante} onChange={setComprobante} />

            {error && (
              <p role="alert" className="text-sm text-red-600">
                {error}
              </p>
            )}

            <button
              type="submit"
              className="rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-700"
            >
              Registrar
            </button>
          </form>
        </Card>

        <Card>
          <CardTitle>Importación masiva</CardTitle>
          <ImportadorMovimientos onImportado={cargarMovimientos} />
        </Card>
      </div>

      <div className="mt-5">
        <Card>
          <CardTitle>Registradas</CardTitle>
          {errorLista && <p className="mt-4 text-sm text-red-600">{errorLista}</p>}
          {!errorLista && movimientos.length === 0 ? (
            <p className="mt-4 text-sm text-gray-500">Aún no has registrado transacciones.</p>
          ) : (
            <ul className="mt-4 divide-y divide-gray-200">
              {movimientos.map((m) => {
                const ingreso = m.tipo === 'INGRESO'
                return (
                  <li key={m.id} className="flex items-center justify-between gap-3 py-2 text-sm">
                    <span className="min-w-0 flex-1">
                      {m.fecha} · {ingreso ? 'Ingreso' : 'Gasto'}
                      {m.categoria ? ` · ${buscarCategoria(m.categoria)?.nombre ?? 'Otros'}` : ''}
                      {m.categoria === 'ahorro' && m.meta_nombre ? ` · Meta: ${m.meta_nombre}` : ''}
                      {m.descripcion ? ` · ${m.descripcion}` : ''}
                    </span>
                    <span className={ingreso ? 'text-green-600' : 'text-red-600'}>
                      {ingreso ? '+' : '-'} {formatearConMoneda(m.monto, m.moneda)}
                    </span>
                    <button
                      type="button"
                      onClick={() => {
                        setErrorEditar('')
                        setEditando(m)
                      }}
                      aria-label="Editar transacción"
                      className="rounded-full p-1.5 text-gray-400 hover:bg-blue-50 hover:text-blue-600"
                    >
                      <Pencil size={16} />
                    </button>
                    <button
                      type="button"
                      onClick={() => {
                        setErrorEliminar('')
                        setPorEliminar(m)
                      }}
                      aria-label="Eliminar transacción"
                      className="rounded-full p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
                    >
                      <Trash2 size={16} />
                    </button>
                  </li>
                )
              })}
            </ul>
          )}
        </Card>
      </div>

      <ModalEliminar
        open={Boolean(porEliminar)}
        detalle={
          porEliminar
            ? `${porEliminar.fecha} · ${porEliminar.tipo === 'INGRESO' ? 'Ingreso' : 'Gasto'}${porEliminar.descripcion ? ` · ${porEliminar.descripcion}` : ''} · ${formatearConMoneda(porEliminar.monto, porEliminar.moneda)}`
            : ''
        }
        eliminando={eliminando}
        error={errorEliminar}
        onConfirmar={confirmarEliminar}
        onCancelar={cancelarEliminar}
      />

      {editando && (
        <FormularioEdicionTransaccion
          key={editando.id}
          movimiento={editando}
          categorias={categorias}
          guardando={guardandoEdicion}
          error={errorEditar}
          onGuardar={guardarEdicion}
          onCancelar={cancelarEdicion}
          metas={metas}
        />
      )}
    </PageContainer>
  )
}

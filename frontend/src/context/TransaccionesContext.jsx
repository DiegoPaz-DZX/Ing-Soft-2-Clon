import { createContext, useContext, useEffect, useState } from 'react'
import { eliminarMovimiento, registrarMovimiento } from '../services/api.js'

const TransaccionesContext = createContext(null)
const CLAVE_TRANSACCIONES = 'kyzen.transacciones'
const MONEDAS_VALIDAS = ['PEN', 'USD']

function cargarTransacciones() {
  try {
    const datos = JSON.parse(localStorage.getItem(CLAVE_TRANSACCIONES) ?? '[]')
    return Array.isArray(datos) ? datos : []
  } catch {
    return []
  }
}

function validarTransaccion({ tipo, monto, fecha, categoria, moneda }) {
  if (!(Number(monto) > 0)) throw new Error('El monto debe ser mayor a 0')
  if (!fecha) throw new Error('La fecha es obligatoria')
  if (tipo === 'gasto' && !categoria) {
    throw new Error('Selecciona una categoría para el gasto')
  }
  if (!MONEDAS_VALIDAS.includes(moneda)) {
    throw new Error('La moneda debe ser Soles o Dólares')
  }
}

function crearTransaccion({ tipo, monto, fecha, categoria, descripcion, comprobante, moneda, metaId }) {
  return {
    id: crypto.randomUUID(),
    backendId: null,
    tipo,
    monto: Number(monto),
    fecha,
    moneda,
    metaId,
    categoria: tipo === 'gasto' ? categoria : null,
    descripcion: descripcion.trim(),
    comprobante: comprobante
      ? { nombre: comprobante.name, tipo: comprobante.type, url: null }
      : null,
  }
}

export function TransaccionesProvider({ children }) {
  const [transacciones, setTransacciones] = useState(cargarTransacciones)

  useEffect(() => {
    localStorage.setItem(CLAVE_TRANSACCIONES, JSON.stringify(transacciones))
  }, [transacciones])

  const registrarTransaccion = (
    tipo, monto, fecha, categoria = '', descripcion = '', comprobante = null, moneda = 'PEN',
    metaId = null,
  ) => {
    const datos = { tipo, monto, fecha, categoria, descripcion, comprobante, moneda, metaId }
    validarTransaccion(datos)
    const nueva = crearTransaccion(datos)

    setTransacciones((actuales) => [nueva, ...actuales])

    return registrarMovimiento({
      tipo: nueva.tipo,
      monto: nueva.monto,
      moneda: nueva.moneda,
      fecha: nueva.fecha,
      descripcion: nueva.descripcion,
      categoria: nueva.categoria ?? '',
      metaId: nueva.metaId,
      comprobante,
    })
      .then((resp) => {
        if (!resp?.id) return
        setTransacciones((actuales) =>
          actuales.map((t) => {
            if (t.id !== nueva.id) return t
            const comprobanteActualizado =
              t.comprobante && resp.comprobante_url
                ? { ...t.comprobante, url: resp.comprobante_url }
                : t.comprobante
            return { ...t, backendId: resp.id, comprobante: comprobanteActualizado }
          }),
        )
      })
      .catch((error) => console.error('No se pudo enviar al backend:', error.message))
  }

  const eliminarTransaccion = async (id) => {
    const transaccion = transacciones.find((t) => t.id === id)
    if (!transaccion) return
    if (transaccion.backendId) {
      await eliminarMovimiento(transaccion.backendId)
    }
    setTransacciones((actuales) => actuales.filter((t) => t.id !== id))
  }

  const quitarPorBackendId = (backendId) => {
    setTransacciones((actuales) => actuales.filter((t) => t.backendId !== backendId))
  }

  const actualizarPorBackendId = (backendId, datos) => {
    setTransacciones((actuales) =>
      actuales.map((transaccion) =>
        transaccion.backendId === backendId
          ? {
              ...transaccion,
              ...datos,
              metaId: datos.meta_id ?? datos.metaId ?? null,
              categoria: datos.categoria ?? transaccion.categoria,
            }
          : transaccion,
      ),
    )
  }

  return (
    <TransaccionesContext.Provider
      value={{
        transacciones,
        registrarTransaccion,
        eliminarTransaccion,
        quitarPorBackendId,
        actualizarPorBackendId,
      }}
    >
      {children}
    </TransaccionesContext.Provider>
  )
}

export function useTransacciones() {
  const contexto = useContext(TransaccionesContext)
  if (!contexto) {
    throw new Error('useTransacciones debe usarse dentro de TransaccionesProvider')
  }
  return contexto
}
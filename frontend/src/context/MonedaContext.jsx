import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { cambiarPreferenciaMoneda, obtenerPreferenciaMoneda } from '../services/api.js'
import { obtenerUsuario } from '../services/sesion.js'

const SOLES = { codigo: 'PEN', nombre: 'Soles', simbolo: 'S/', solesPorUnidad: 1 }

const MonedaContext = createContext(null)

export function MonedaProvider({ children }) {
  const cuenta = obtenerUsuario()?.id
  const [divisa, setDivisa] = useState(SOLES)
  const [opciones, setOpciones] = useState([SOLES])
  const [tipoCambio, setTipoCambio] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    let activo = true
    if (!cuenta) {
      setCargando(false)
      return
    }
    obtenerPreferenciaMoneda()
      .then((datos) => {
        if (!activo) return
        setDivisa(datos.divisa)
        setOpciones(datos.opciones)
        setTipoCambio(datos.tipoCambio)
      })
      .catch(() => {})
      .finally(() => {
        if (activo) setCargando(false)
      })
    return () => {
      activo = false
    }
  }, [cuenta])

  const cambiarDivisa = useCallback(
    async (codigo) => {
      const datos = await cambiarPreferenciaMoneda(codigo)
      setDivisa(datos.divisa)
      setOpciones(datos.opciones)
      setTipoCambio(datos.tipoCambio)
      return datos.divisa
    },
    [cuenta],
  )

  const valor = useMemo(() => {
    const conDosDecimales = (numero) =>
      numero.toLocaleString('es-PE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    const convertirMovimiento = (monto, moneda = 'PEN') => {
      const valor = Number(monto)

      if (moneda === divisa.codigo) {
        return valor
      }

      if (moneda === 'PEN') {
        return valor / divisa.solesPorUnidad
      }

      if (moneda === 'USD' && tipoCambio) {
        const montoEnSoles = valor * tipoCambio.solesPorDolar
        return montoEnSoles / divisa.solesPorUnidad
      }

      return valor
    }
    const convertir = (montoEnSoles) => Number(montoEnSoles) / divisa.solesPorUnidad
    const formatear = (montoEnSoles) => `${divisa.simbolo} ${conDosDecimales(convertir(montoEnSoles))}`
    const formatearMovimiento = (monto, moneda = 'PEN') => {
      const valorConvertido = convertirMovimiento(monto, moneda)
      return `${divisa.simbolo} ${conDosDecimales(valorConvertido)}`
    }
    return {
      divisa,
      opciones,
      tipoCambio,
      cargando,
      cambiarDivisa,
      convertir,
      convertirMovimiento,
      formatear,
      formatearMovimiento,
    }
  }, [divisa, opciones, tipoCambio, cargando, cambiarDivisa])

  return <MonedaContext.Provider value={valor}>{children}</MonedaContext.Provider>
}

export function useMoneda() {
  const contexto = useContext(MonedaContext)
  if (!contexto) {
    throw new Error('useMoneda debe usarse dentro de MonedaProvider')
  }
  return contexto
}

import { obtenerUsuario } from './sesion.js'

const URL_DJANGO = 'http://localhost:8000'
const JSON_HEADERS = { 'Content-Type': 'application/json' }

function headersAutenticados(headers = {}) {
  const usuario = obtenerUsuario()
  return {
    ...headers,
    Authorization: usuario?.token ? `Bearer ${usuario.token}` : '',
  }
}

function opcionesJson(method, datos) {
  return { method, headers: JSON_HEADERS, body: JSON.stringify(datos) }
}

async function pedir(ruta, opciones, base = URL_DJANGO) {
  let respuesta
  try {
    respuesta = await fetch(base + ruta, opciones)
  } catch {
    const error = new Error('No se pudo conectar con el servidor. ¿Está corriendo el backend?')
    error.name = 'ErrorConexion'
    throw error
  }

  const datos = await respuesta.json().catch(() => null)
  if (!respuesta.ok) {
    const error = new Error(datos?.error ?? `Error ${respuesta.status}`)
    error.detalles = datos?.errores ?? []
    throw error
  }
  return datos
}

function parametrosReporte({ desde, hasta, graficos = true, analisis = true } = {}) {
  const params = new URLSearchParams()
  if (desde || hasta) {
    params.set('desde', desde ?? '')
    params.set('hasta', hasta ?? '')
  }
  if (!graficos) params.set('graficos', '0')
  if (!analisis) params.set('analisis', '0')
  return params
}

export function obtenerBalance() {
  return pedir('/api/balance', {headers: headersAutenticados()}, URL_DJANGO)
}

export function obtenerTips() {
  return pedir('/api/tips', undefined, URL_DJANGO)
}

export function obtenerRecomendaciones() {
  return pedir(
    '/api/recomendaciones',
    { headers: headersAutenticados() },
    URL_DJANGO,
  )
}

export function obtenerCategorias() {
  return pedir('/api/categorias', undefined, URL_DJANGO)
}

export function registrarCuenta(datos) {
  return pedir('/api/registro', opcionesJson('POST', datos), URL_DJANGO)
}

export function obtenerMovimientos(rango) {
  if (!rango) return pedir('/api/movimientos', {headers:headersAutenticados()}, URL_DJANGO)
  const params = new URLSearchParams({ desde: rango.desde ?? '', hasta: rango.hasta ?? '' })
  return pedir(`/api/movimientos?${params}`, {headers: headersAutenticados()}, URL_DJANGO)
}

export function iniciarSesion(correo, clave) {
  return pedir('/api/login', opcionesJson('POST', { correo, clave }), URL_DJANGO)
}

function opcionesAdmin(token, method, datos) {
  return {
    ...opcionesJson(method, datos),
    headers: { ...JSON_HEADERS, Authorization: `Bearer ${token}` },
  }
}

export function obtenerUsuariosAdmin(token) {
  return pedir('/api/admin/usuarios', {
    headers: { Authorization: `Bearer ${token}` },
  }, URL_DJANGO)
}

export function cambiarRolUsuario(token, cuentaId, rol) {
  return pedir(
    `/api/admin/usuarios/${cuentaId}/rol`,
    opcionesAdmin(token, 'PUT', { rol }),
    URL_DJANGO,
  )
}

export function generarCodigoCambio(correo) {
  return pedir(
    '/api/cambiar-clave',
    opcionesJson('POST', { accion: 'generar', correo }),
    URL_DJANGO,
  )
}

export function cambiarClave(correo, codigo, nuevaClave, confirmacionClave) {
  return pedir(
    '/api/cambiar-clave',
    opcionesJson('POST', {
      accion: 'cambiar',
      correo,
      codigo,
      nueva_clave: nuevaClave,
      confirmacion_clave: confirmacionClave,
    }),
    URL_DJANGO,
  )
}

export function obtenerMetas() {
  return pedir('/api/metas', { headers: headersAutenticados() }, URL_DJANGO)
}

export function crearMeta(nombre, objetivoPEN) {
  return pedir(
    '/api/metas',
    { ...opcionesJson('POST', { nombre, objetivo_pen: objetivoPEN }), headers: headersAutenticados(JSON_HEADERS) },
    URL_DJANGO,
  )
}

export function abonarMeta(metaId, montoPEN) {
  return pedir(
    `/api/metas/${metaId}/abonos`,
    { ...opcionesJson('POST', { monto_pen: montoPEN }), headers: headersAutenticados(JSON_HEADERS) },
    URL_DJANGO,
  )
}

export function eliminarMeta(metaId) {
  return pedir(
    `/api/metas/${metaId}`,
    { method: 'DELETE', headers: headersAutenticados() },
    URL_DJANGO,
  )
}

export function renombrarMeta(metaId, nombre) {
  return pedir(
    `/api/metas/${metaId}`,
    {
      ...opcionesJson('PUT', { nombre }),
      headers: headersAutenticados(JSON_HEADERS),
    },
    URL_DJANGO,
  )
}

export function obtenerPreferenciaMoneda() {
  return pedir('/api/preferencias/moneda', { headers: headersAutenticados() }, URL_DJANGO)
}

export function cambiarPreferenciaMoneda(divisa) {
  return pedir(
    '/api/preferencias/moneda',
    { ...opcionesJson('PUT', { divisa }), headers: headersAutenticados(JSON_HEADERS) },
    URL_DJANGO,
  )
}

export function obtenerReporteFinanciero(opciones = {}) {
  const params = parametrosReporte(opciones).toString()
  return pedir(`/api/reportes/financiero${params ? `?${params}` : ''}`, {headers: headersAutenticados()} , URL_DJANGO)
}

export function urlExportarReporte(opciones, formato) {
  const params = parametrosReporte(opciones)
  params.set('formato', formato)
  return `${URL_DJANGO}/api/reportes/financiero?${params}`
}

async function descargarArchivo(ruta, formato) {
  let respuesta
  try {
    respuesta = await fetch(ruta, { headers: headersAutenticados() })
  } catch {
    throw new Error('No se pudo conectar con el servidor. ¿Está corriendo el backend?')
  }
  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => null)
    throw new Error(datos?.error ?? `No se pudo descargar el reporte (error ${respuesta.status}).`)
  }
  const archivo = await respuesta.blob()
  const urlTemporal = URL.createObjectURL(archivo)
  const enlace = document.createElement('a')
  enlace.href = urlTemporal
  enlace.download = `reporte-financiero-kyzen.${formato}`
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  URL.revokeObjectURL(urlTemporal)
}

export function descargarReporteFinanciero(opciones, formato) {
  return descargarArchivo(urlExportarReporte(opciones, formato), formato)
}

export function registrarMovimiento({
  tipo,
  monto,
  fecha,
  descripcion = '',
  categoria = '',
  moneda = 'PEN',
  comprobante = null,
  metaId = null,
}) {
  if (comprobante) {
    const formData = new FormData()
    formData.append('tipo', tipo)
    formData.append('monto', monto)
    formData.append('moneda', moneda)
    formData.append('fecha', fecha)
    formData.append('descripcion', descripcion)
    formData.append('categoria', categoria)
    if (metaId) formData.append('meta_id', metaId)
    formData.append('comprobante', comprobante)
    return pedir(
      '/api/movimientos/nuevo',
      { method: 'POST', headers: headersAutenticados(), body: formData },
      URL_DJANGO,
    )
  }

  return pedir(
    '/api/movimientos/nuevo',
    {
      ...opcionesJson('POST', { tipo, monto, moneda, fecha, descripcion, categoria, meta_id: metaId }),
      headers: headersAutenticados(JSON_HEADERS),
    },
    URL_DJANGO,
  )
}

// HU20
export function importarMovimientos(archivo) {
  const formData = new FormData()
  formData.append('archivo', archivo)
  return pedir(
    '/api/movimientos/importar',
    { method: 'POST', headers: headersAutenticados(), body: formData },
    URL_DJANGO,
  )
}

export function urlDjango(ruta) {
  if (!ruta) return null
  if (ruta.startsWith('file:')) return null
  return ruta.startsWith('http') ? ruta : URL_DJANGO + ruta
}

export function eliminarMovimiento(id) {
  return pedir(`/api/movimientos/${id}/eliminar`, {method: 'DELETE', headers: headersAutenticados()}, URL_DJANGO)
}

export function editarMovimiento(id, datos) {
  return pedir(`/api/movimientos/${id}/editar`, {method: 'PUT', headers: headersAutenticados(JSON_HEADERS), body: JSON.stringify(datos)}, URL_DJANGO)
}

// HU28: monitor analítico de salud financiera
export function obtenerMonitorSalud() {
  return pedir('/api/monitor/salud', { headers: headersAutenticados() }, URL_DJANGO)
}

import { obtenerUsuario } from './sesion.js'

const URL_DJANGO = 'http://localhost:8000'
const MENSAJE_ERROR = 'No se pudo generar el reporte, intente más tarde'

// Pide el reporte mensual al backend (con la sesión del usuario) y lo descarga.
// El backend lo genera en la divisa de visualización que el usuario tiene activa.
export async function descargarReporteMensual({ anio, mes, formato }) {
  const usuario = obtenerUsuario()
  const params = new URLSearchParams({ anio, mes, formato })

  let respuesta
  try {
    respuesta = await fetch(`${URL_DJANGO}/api/reportes/financiero/exportar?${params}`, {
      headers: { Authorization: usuario?.token ? `Bearer ${usuario.token}` : '' },
    })
  } catch {
    throw new Error(MENSAJE_ERROR)
  }

  if (!respuesta.ok) {
    const datos = await respuesta.json().catch(() => null)
    throw new Error(datos?.error ?? MENSAJE_ERROR)
  }

  const archivo = await respuesta.blob()
  guardarArchivo(archivo, nombreDelArchivo(respuesta, anio, mes, formato))
}

function nombreDelArchivo(respuesta, anio, mes, formato) {
  const cabecera = respuesta.headers.get('Content-Disposition') ?? ''
  const coincidencia = cabecera.match(/filename=([^;]+)/)
  if (coincidencia) return coincidencia[1].trim()
  return `reporte-${anio}-${mes}.${formato === 'excel' ? 'xlsx' : 'pdf'}`
}

function guardarArchivo(archivo, nombre) {
  const url = URL.createObjectURL(archivo)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  document.body.appendChild(enlace)
  enlace.click()
  enlace.remove()
  URL.revokeObjectURL(url)
}
import { obtenerUsuario } from './sesion.js'

const URL_BASE_DJANGO = 'http://localhost:8000'

function cabeceras(extra = {}) {
  const usuario = obtenerUsuario()
  return { ...extra, Authorization: usuario?.token ? `Bearer ${usuario.token}` : '' }
}

export const ServicioAlertas = {
  async obtenerAlertas() {
    try {
      const respuesta = await fetch(`${URL_BASE_DJANGO}/api/alertas`, { headers: cabeceras() })
      if (!respuesta.ok) return []
      return (await respuesta.json()) || []
    } catch {
      return []
    }
  },

  async establecerLimite(categoria, limiteMensual) {
    const respuesta = await fetch(`${URL_BASE_DJANGO}/api/limites`, {
      method: 'POST',
      headers: cabeceras({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ categoria, limite_mensual: limiteMensual }),
    })
    const datos = await respuesta.json()
    if (!respuesta.ok || !datos.exito) {
      throw new Error(datos.error || 'Error al establecer el límite')
    }
    return datos
  },

  async obtenerLimites() {
    try {
      const respuesta = await fetch(`${URL_BASE_DJANGO}/api/limites`, { headers: cabeceras() })
      if (!respuesta.ok) return {}
      return (await respuesta.json()) || {}
    } catch {
      return {}
    }
  },
}

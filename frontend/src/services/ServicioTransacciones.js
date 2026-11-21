import { api } from './api.js'

export const ServicioTransacciones = {
  async editarTransaccion(movimientoId, datos) {
    try {
      return (await api.put(`/movimientos/${movimientoId}/editar`, datos)).data
    } catch (err) {
      throw new Error(err.response?.data?.error || 'Error al editar transacción')
    }
  },
  
  async obtenerTransaccion(movimientoId) {
    try {
      return (await api.get(`/movimientos/${movimientoId}`)).data
    } catch {
      return null
    }
  }
}
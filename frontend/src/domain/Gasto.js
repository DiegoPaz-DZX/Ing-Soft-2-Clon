import { buscarCategoria } from './categorias.js'

function crearId() {
  return globalThis.crypto?.randomUUID?.() ?? `gasto-${Date.now()}`
}

export default class Gasto {
  constructor({ id, descripcion, monto, fecha, categoria, registradoEn }) {
    this.id = id
    this.descripcion = descripcion
    this.monto = monto
    this.fecha = fecha
    this.categoria = categoria
    this.registradoEn = registradoEn
  }

  static crear({ descripcion, monto, fecha, categoria }) {
    const descripcionLimpia = descripcion.trim()
    const montoNumerico = Number(monto)

    if (!descripcionLimpia) throw new Error('Ingresa una descripción.')
    if (!Number.isFinite(montoNumerico) || montoNumerico <= 0) {
      throw new Error('El monto debe ser mayor a cero.')
    }
    if (!fecha) throw new Error('Selecciona una fecha.')
    if (!buscarCategoria(categoria)) throw new Error('Selecciona una categoría válida.')

    return new Gasto({
      id: crearId(),
      descripcion: descripcionLimpia,
      monto: Math.round(montoNumerico * 100) / 100,
      fecha,
      categoria,
      registradoEn: new Date().toISOString(),
    })
  }
}

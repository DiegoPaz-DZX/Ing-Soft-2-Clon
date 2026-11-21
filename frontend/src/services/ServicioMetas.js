import MetaAhorro from '../domain/MetaAhorro.js'

// El repositorio se inyecta: el servicio no sabe si las metas viven en localStorage o en un backend
export default class ServicioMetas {
  constructor(repositorio) {
    this.repositorio = repositorio
  }

  async obtener() {
    return this.repositorio.obtener()
  }

  // `objetivo` llega en la divisa activa; el conversor lo lleva a soles para guardarlo
  async crear({ nombre, objetivo }, conversor) {
    const meta = MetaAhorro.crear({ nombre, objetivoPEN: conversor.aSoles(objetivo) })
    return this.repositorio.guardar(meta)
  }

  async abonar(meta, monto, conversor) {
    if (!meta) throw new Error('Registra una meta antes de abonar.')
    if (meta.id && this.repositorio.abonar) {
      return this.repositorio.abonar(meta, conversor.aSoles(monto))
    }
    return this.repositorio.guardar(meta.abonar(conversor.aSoles(monto)))
  }

  async eliminar(meta) {
    if (!meta?.id) throw new Error('La meta no existe.')
    return this.repositorio.eliminar(meta)
  }

  async renombrar(meta, nombre) {
    if (!meta?.id) throw new Error('La meta no existe.')
    const nombreLimpio = String(nombre ?? '').trim()
    if (!nombreLimpio) throw new Error('Escribe un nombre para la meta.')
    return this.repositorio.renombrar(meta, nombreLimpio)
  }

  // Todo en soles; la vista lo convierte a la divisa activa al mostrarlo
  calcularProgreso(meta, transacciones, solesPorDolar) {
    const ahorroPorGastos = transacciones
      .filter((t) => String(t.tipo).toLowerCase() === 'gasto')
      .filter((t) => String(t.categoria).toLowerCase() === 'ahorro')
      .filter((t) => Number(t.metaId ?? t.meta_id) === Number(meta.id))
      .reduce((total, t) => {
        const monto = Number(t.monto)
        return total + (t.moneda === 'USD' ? monto * solesPorDolar : monto)
      }, 0)

    const ahorradoPEN = meta.totalAbonadoPEN + ahorroPorGastos
    return {
      ahorradoPEN,
      objetivoPEN: meta.objetivoPEN,
      faltantePEN: Math.max(meta.objetivoPEN - ahorradoPEN, 0),
      porcentaje: Math.min((ahorradoPEN / meta.objetivoPEN) * 100, 100),
      completada: ahorradoPEN >= meta.objetivoPEN,
    }
  }
}

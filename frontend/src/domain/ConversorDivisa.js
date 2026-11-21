// Convierte entre soles (moneda de almacenamiento) y la divisa activa del perfil
export default class ConversorDivisa {
  constructor({ solesPorUnidad = 1 } = {}) {
    if (!(Number(solesPorUnidad) > 0)) throw new Error('El tipo de cambio debe ser mayor que cero.')
    this.solesPorUnidad = Number(solesPorUnidad)
  }

  deSoles(montoPEN) {
    return Number(montoPEN) / this.solesPorUnidad
  }

  aSoles(montoEnDivisa) {
    return Number(montoEnDivisa) * this.solesPorUnidad
  }
}

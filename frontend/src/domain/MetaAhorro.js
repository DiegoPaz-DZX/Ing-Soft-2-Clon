function crearId() {
  return globalThis.crypto?.randomUUID?.() ?? `abono-${Date.now()}`
}

function validarMonto(monto, mensaje) {
  const numero = Number(monto)
  if (!Number.isFinite(numero) || numero <= 0) throw new Error(mensaje)
  return numero
}

// Los montos se guardan siempre en soles (PEN). La divisa activa solo afecta cómo se muestran.
export default class MetaAhorro {
  constructor({ id = null, nombre, objetivoPEN, totalAbonadoPEN = 0, abonos = [] }) {
    this.id = id
    this.nombre = nombre
    this.objetivoPEN = objetivoPEN
    this.totalAbonadoPEN = Number(totalAbonadoPEN)
    this.abonos = abonos
  }

  static crear({ nombre, objetivoPEN }) {
    const nombreLimpio = String(nombre ?? '').trim()
    if (!nombreLimpio) throw new Error('Escribe un nombre para la meta.')
    const objetivo = validarMonto(objetivoPEN, 'El monto objetivo debe ser mayor que cero.')
    return new MetaAhorro({ nombre: nombreLimpio, objetivoPEN: objetivo })
  }

  // Acepta el formato anterior ({ nombre, objetivo, moneda: 'PEN' }) para no perder metas guardadas
  static desdeJSON(datos) {
    if (!datos) return null
    return new MetaAhorro({
      id: datos.id ?? null,
      nombre: datos.nombre,
      objetivoPEN: datos.objetivoPEN ?? datos.objetivo,
      totalAbonadoPEN: datos.totalAbonadoPEN ?? 0,
      abonos: datos.abonos ?? [],
    })
  }

  abonar(montoPEN) {
    const monto = validarMonto(montoPEN, 'El abono debe ser mayor que cero.')
    const abono = { id: crearId(), montoPEN: monto, fecha: new Date().toISOString() }
    return new MetaAhorro({
      ...this,
      totalAbonadoPEN: this.totalAbonadoPEN + monto,
      abonos: [...this.abonos, abono],
    })
  }

}

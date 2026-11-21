export const TipoTransaccion = Object.freeze({
  INGRESO: 'ingreso',
  GASTO: 'gasto',
})

// NUEVO: tipos y tamaño permitidos para el comprobante
export const COMPROBANTE_TIPOS = Object.freeze(['image/jpeg', 'image/png', 'application/pdf'])
export const COMPROBANTE_MAX_MB = 5

// NUEVO: lanza un Error si el archivo no es válido
export function validarComprobante(archivo) {
  if (!COMPROBANTE_TIPOS.includes(archivo.type)) {
    throw new Error('Solo se permiten archivos JPG, PNG o PDF')
  }
  if (archivo.size > COMPROBANTE_MAX_MB * 1024 * 1024) {
    throw new Error(`El archivo no puede superar los ${COMPROBANTE_MAX_MB} MB`)
  }
}

export class Transaccion {
  #id
  #tipo
  #monto
  #fecha
  #moneda
  #comprobante // NUEVO

  // NUEVO: se agrega "comprobante" al final del constructor que ya existía
  constructor(tipo, monto, fecha, moneda = 'PEN', id = crypto.randomUUID(), comprobante = null) {
    if (!Object.values(TipoTransaccion).includes(tipo)) {
      throw new Error('El tipo debe ser ingreso o gasto')
    }
    if (!(Number(monto) > 0)) {
      throw new Error('El monto debe ser mayor a 0')
    }
    if (!fecha) {
      throw new Error('La fecha es obligatoria')
    }
    if (comprobante) validarComprobante(comprobante) // NUEVO

    this.#id = id
    this.#tipo = tipo
    this.#monto = Number(monto)
    this.#fecha = fecha
    this.#moneda = moneda
    this.#comprobante = comprobante // NUEVO
  }

  // Getters
  getId() {
    return this.#id
  }

  getTipo() {
    return this.#tipo
  }

  getMonto() {
    return this.#monto
  }

  getFecha() {
    return this.#fecha
  }

  getMoneda() {
    return this.#moneda
  }

  // NUEVO
  getComprobante() {
    return this.#comprobante
  }

  // NUEVO
  tieneComprobante() {
    return this.#comprobante !== null
  }

  esIngreso() {
    return this.#tipo === TipoTransaccion.INGRESO
  }

  esGasto() {
    return this.#tipo === TipoTransaccion.GASTO
  }
}
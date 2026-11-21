export class LibroDeCaja {
  #transacciones

  constructor(transacciones = []) {
    this.#transacciones = [...transacciones]
  }

  // Devuelve un LibroDeCaja nuevo, para que React detecte el cambio
  registrar(transaccion) {
    return new LibroDeCaja([transaccion, ...this.#transacciones])
  }

  getTransacciones() {
    return [...this.#transacciones]
  }

  calcularIngresos() {
    return this.#sumar((t) => t.esIngreso())
  }

  calcularGastos() {
    return this.#sumar((t) => t.esGasto())
  }

  calcularBalance() {
    return this.calcularIngresos() - this.calcularGastos()
  }

  #sumar(criterio) {
    return this.#transacciones
      .filter(criterio)
      .reduce((total, t) => total + t.getMonto(), 0)
  }
}
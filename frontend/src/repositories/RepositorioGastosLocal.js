const CLAVE_GASTOS = 'kyzen.gastos'

export default class RepositorioGastosLocal {
  constructor(almacenamiento = globalThis.localStorage) {
    this.almacenamiento = almacenamiento
  }

  listar() {
    if (!this.almacenamiento) return []

    try {
      const datos = JSON.parse(this.almacenamiento.getItem(CLAVE_GASTOS) ?? '[]')
      return Array.isArray(datos) ? datos : []
    } catch {
      return []
    }
  }

  guardar(gastos) {
    if (!this.almacenamiento) return
    this.almacenamiento.setItem(CLAVE_GASTOS, JSON.stringify(gastos))
  }
}

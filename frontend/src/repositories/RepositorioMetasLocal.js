import MetaAhorro from '../domain/MetaAhorro.js'

const CLAVE = 'kyzen.meta'

export default class RepositorioMetasLocal {
  constructor(almacen = globalThis.localStorage) {
    this.almacen = almacen
  }

  obtener() {
    try {
      return MetaAhorro.desdeJSON(JSON.parse(this.almacen.getItem(CLAVE) ?? 'null'))
    } catch {
      return null
    }
  }

  guardar(meta) {
    this.almacen.setItem(CLAVE, JSON.stringify(meta))
    return meta
  }
}

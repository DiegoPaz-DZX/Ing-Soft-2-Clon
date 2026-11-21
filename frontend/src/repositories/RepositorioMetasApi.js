import { abonarMeta, crearMeta, eliminarMeta, obtenerMetas, renombrarMeta } from '../services/api.js'
import MetaAhorro from '../domain/MetaAhorro.js'

function convertir(datos) {
  return MetaAhorro.desdeJSON(datos)
}

export default class RepositorioMetasApi {
  async obtener() {
    const respuesta = await obtenerMetas()
    return (respuesta.metas ?? []).map(convertir)
  }

  async guardar(meta) {
    if (meta.id) return meta
    const datos = await crearMeta(meta.nombre, meta.objetivoPEN)
    return convertir(datos)
  }

  async abonar(meta, montoPEN) {
    const datos = await abonarMeta(meta.id, montoPEN)
    return convertir(datos)
  }

  async eliminar(meta) {
    await eliminarMeta(meta.id)
  }

  async renombrar(meta, nombre) {
    const datos = await renombrarMeta(meta.id, nombre)
    return convertir(datos)
  }
}

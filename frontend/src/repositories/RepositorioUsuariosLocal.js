const CLAVE_USUARIOS = 'kyzen.usuarios'

export default class RepositorioUsuariosLocal {
  constructor(almacenamiento = globalThis.localStorage) {
    this.almacenamiento = almacenamiento
  }

  listar() {
    if (!this.almacenamiento) return []

    try {
      const datos = JSON.parse(this.almacenamiento.getItem(CLAVE_USUARIOS) ?? '[]')
      return Array.isArray(datos) ? datos : []
    } catch {
      return []
    }
  }

  buscarPorCorreo(correo) {
    return this.listar().find((usuario) => usuario.correo === correo)
  }

  guardar(usuario) {
    if (!this.almacenamiento) return
    this.almacenamiento.setItem(CLAVE_USUARIOS, JSON.stringify([...this.listar(), usuario]))
  }
}

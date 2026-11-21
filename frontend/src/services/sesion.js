const CLAVE = 'kyzen.usuario'

export function guardarUsuario(usuario) {
  try {
    sessionStorage.setItem(CLAVE, JSON.stringify(usuario))
  } catch {
  }
}

export function obtenerUsuario() {
  try {
    return JSON.parse(sessionStorage.getItem(CLAVE))
  } catch {
    return null
  }
}

export function cerrarSesion() {
  sessionStorage.removeItem('kyzen.usuario')
  localStorage.removeItem('kyzen.transacciones')
}

export async function cerrarSesionRemota() {
  const usuario = obtenerUsuario()
  try {
    if (usuario?.token) {
      await fetch('http://localhost:8000/api/logout', {
        method: 'POST',
        headers: { Authorization: 'Bearer ' + usuario.token },
      })
    }
  } finally {
    cerrarSesion()
  }
}
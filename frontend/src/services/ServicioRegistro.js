export function validarDatosRegistro({ correo, clave, confirmacion }) {
  const errores = {}
  const correoLimpio = correo.trim()

  if (!correoLimpio) errores.correo = 'Ingresa tu correo.'
  else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correoLimpio)) {
    errores.correo = 'Ingresa un correo válido.'
  }

  if (!clave) errores.clave = 'Ingresa una contraseña.'
  else if (clave.length < 8 || !/[A-Za-z]/.test(clave) || !/\d/.test(clave)) {
    errores.clave = 'Usa al menos 8 caracteres, una letra y un número.'
  }

  if (!confirmacion) errores.confirmacion = 'Confirma tu contraseña.'
  else if (clave !== confirmacion) errores.confirmacion = 'Las contraseñas no coinciden.'

  return errores
}

async function obtenerHash(clave, salt) {
  const datos = new TextEncoder().encode(`${salt}:${clave}`)
  const hash = await globalThis.crypto.subtle.digest('SHA-256', datos)
  return Array.from(new Uint8Array(hash), (byte) => byte.toString(16).padStart(2, '0')).join('')
}

export class ErrorRegistro extends Error {
  constructor(mensaje, campos = {}) {
    super(mensaje)
    this.campos = campos
  }
}

export default class ServicioRegistro {
  constructor(repositorio, registroRemoto = null) {
    this.repositorio = repositorio
    this.registroRemoto = registroRemoto
  }

  async registrar(datos) {
    const errores = validarDatosRegistro(datos)
    if (Object.keys(errores).length > 0) {
      throw new ErrorRegistro('Revisa los datos del formulario.', errores)
    }

    const correo = datos.correo.trim().toLowerCase()
    if (!this.registroRemoto && this.repositorio.buscarPorCorreo(correo)) {
      throw new ErrorRegistro('Este correo ya está registrado.', {
        correo: 'Este correo ya está registrado.',
      })
    }

    const salt = globalThis.crypto.randomUUID()
    const usuario = {
      id: globalThis.crypto.randomUUID(),
      correo,
      claveHash: await obtenerHash(datos.clave, salt),
      salt,
      creadoEn: new Date().toISOString(),
    }

    if (this.registroRemoto) {
      try {
        const remoto = await this.registroRemoto(datos)
        return { id: remoto.id, correo: remoto.correo }
      } catch (error) {
        const esCorreoRepetido = error.message.toLowerCase().includes('registrado')
        const campos = esCorreoRepetido
          ? { correo: error.message }
          : { general: error.message }
        throw new ErrorRegistro(error.message, campos)
      }
    }

    this.repositorio.guardar(usuario)
    return { id: usuario.id, correo: usuario.correo }
  }
}

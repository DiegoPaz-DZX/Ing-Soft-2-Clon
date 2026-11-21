import test from 'node:test'
import assert from 'node:assert/strict'
import ServicioRegistro, {
  ErrorRegistro,
  validarDatosRegistro,
} from '../src/services/ServicioRegistro.js'

class RepositorioUsuariosMemoria {
  constructor() {
    this.usuarios = []
  }

  buscarPorCorreo(correo) {
    return this.usuarios.find((usuario) => usuario.correo === correo)
  }

  guardar(usuario) {
    this.usuarios.push(usuario)
  }
}

test('acepta un correo y contraseña válidos', () => {
  const errores = validarDatosRegistro({
    correo: 'eduardo@correo.com',
    clave: 'Kyzen2026',
    confirmacion: 'Kyzen2026',
  })

  assert.deepEqual(errores, {})
})

test('rechaza contraseñas distintas o débiles', () => {
  const errores = validarDatosRegistro({
    correo: 'correo-invalido',
    clave: '123',
    confirmacion: '456',
  })

  assert.ok(errores.correo)
  assert.ok(errores.clave)
  assert.ok(errores.confirmacion)
})

test('guarda el hash pero no la contraseña original', async () => {
  const repositorio = new RepositorioUsuariosMemoria()
  const servicio = new ServicioRegistro(repositorio)

  await servicio.registrar({
    correo: 'eduardo@correo.com',
    clave: 'Kyzen2026',
    confirmacion: 'Kyzen2026',
  })

  assert.equal(repositorio.usuarios.length, 1)
  assert.equal(repositorio.usuarios[0].clave, undefined)
  assert.notEqual(repositorio.usuarios[0].claveHash, 'Kyzen2026')
})

test('usa el registro del backend cuando está configurado', async () => {
  const repositorio = new RepositorioUsuariosMemoria()
  const registroRemoto = async ({ correo }) => ({ id: 25, correo: correo.toLowerCase() })
  const servicio = new ServicioRegistro(repositorio, registroRemoto)

  const cuenta = await servicio.registrar({
    correo: 'Eduardo@correo.com',
    clave: 'Kyzen2026',
    confirmacion: 'Kyzen2026',
  })

  assert.deepEqual(cuenta, { id: 25, correo: 'eduardo@correo.com' })
  assert.equal(repositorio.usuarios.length, 0)
})

test('muestra el correo repetido como error del formulario', async () => {
  const registroRemoto = async () => {
    throw new Error('Este correo ya está registrado.')
  }
  const servicio = new ServicioRegistro(new RepositorioUsuariosMemoria(), registroRemoto)

  await assert.rejects(
    () =>
      servicio.registrar({
        correo: 'eduardo@correo.com',
        clave: 'Kyzen2026',
        confirmacion: 'Kyzen2026',
      }),
    (error) => error instanceof ErrorRegistro && Boolean(error.campos.correo),
  )
})

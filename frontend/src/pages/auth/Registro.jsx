import { useState } from 'react'
import { Link } from 'react-router-dom'
import { LockKeyhole, Mail, UserPlus } from 'lucide-react'
import { Button, Card, Input } from '../../components/ui'
import { PATHS } from '../../routes/paths.js'
import RepositorioUsuariosLocal from '../../repositories/RepositorioUsuariosLocal.js'
import ServicioRegistro, { ErrorRegistro } from '../../services/ServicioRegistro.js'
import { registrarCuenta } from '../../services/api.js'

const servicioRegistro = new ServicioRegistro(new RepositorioUsuariosLocal(), registrarCuenta)

const FORMULARIO_INICIAL = {
  correo: '',
  clave: '',
  confirmacion: '',
}

export default function Registro() {
  const [formulario, setFormulario] = useState(FORMULARIO_INICIAL)
  const [errores, setErrores] = useState({})
  const [mensaje, setMensaje] = useState('')
  const [enviando, setEnviando] = useState(false)

  function actualizar(campo, valor) {
    setFormulario((anterior) => ({ ...anterior, [campo]: valor }))
    setErrores((anteriores) => ({ ...anteriores, [campo]: '' }))
    setMensaje('')
  }

  async function registrar(event) {
    event.preventDefault()
    setEnviando(true)
    setErrores({})
    setMensaje('')

    try {
      const usuario = await servicioRegistro.registrar(formulario)
      setFormulario(FORMULARIO_INICIAL)
      setMensaje(`Cuenta creada para ${usuario.correo}. Ya puedes iniciar sesión.`)
    } catch (problema) {
      if (problema instanceof ErrorRegistro) setErrores(problema.campos)
      else setErrores({ general: 'No se pudo crear la cuenta. Intenta nuevamente.' })
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Card className="p-8">
      <h1 className="text-xl font-bold">Crear cuenta</h1>
      <p className="mb-6 text-xs text-muted">Tu perfil financiero privado y seguro.</p>

      <form className="space-y-4" onSubmit={registrar} noValidate>
        <div>
          <Input
            label="Correo"
            icon={Mail}
            type="email"
            autoComplete="email"
            placeholder="nombre@correo.com"
            value={formulario.correo}
            onChange={(event) => actualizar('correo', event.target.value)}
          />
          {errores.correo && <p className="mt-1 text-xs text-expense">{errores.correo}</p>}
        </div>

        <div>
          <Input
            label="Contraseña"
            icon={LockKeyhole}
            type="password"
            autoComplete="new-password"
            placeholder="Mínimo 8 caracteres"
            value={formulario.clave}
            onChange={(event) => actualizar('clave', event.target.value)}
          />
          {errores.clave ? (
            <p className="mt-1 text-xs text-expense">{errores.clave}</p>
          ) : (
            <p className="mt-1 text-[10px] text-muted">Incluye al menos una letra y un número.</p>
          )}
        </div>

        <div>
          <Input
            label="Confirmar contraseña"
            icon={LockKeyhole}
            type="password"
            autoComplete="new-password"
            placeholder="Repite tu contraseña"
            value={formulario.confirmacion}
            onChange={(event) => actualizar('confirmacion', event.target.value)}
          />
          {errores.confirmacion && (
            <p className="mt-1 text-xs text-expense">{errores.confirmacion}</p>
          )}
        </div>

        {errores.general && (
          <p role="alert" className="rounded-xl bg-expense-soft px-3 py-2 text-xs text-expense">
            {errores.general}
          </p>
        )}
        {mensaje && (
          <p role="status" className="rounded-xl bg-income-soft px-3 py-2 text-xs text-income">
            {mensaje}
          </p>
        )}

        <Button type="submit" block disabled={enviando}>
          <UserPlus size={15} /> {enviando ? 'Creando cuenta...' : 'Registrarme'}
        </Button>
      </form>

      <p className="mt-6 text-center text-xs text-muted">
        ¿Ya tienes cuenta?{' '}
        <Link to={PATHS.login} className="font-semibold text-primary">
          Inicia sesión
        </Link>
      </p>
    </Card>
  )
}

import { useState } from 'react'
import { Link } from 'react-router-dom'
import { KeyRound, LockKeyhole, Mail } from 'lucide-react'
import { Button, Card, Input } from '../../components/ui/index.js'
import { PATHS } from '../../routes/paths.js'
import { cambiarClave, generarCodigoCambio } from '../../services/api.js'

const PASOS = { correo: 1, codigo: 2, clave: 3, terminado: 4 }

function validarClave(clave, confirmacion) {
  if (clave.length < 8) return 'La contraseña debe tener al menos 8 caracteres.'
  if (clave !== confirmacion) return 'Las contraseñas no coinciden.'
  return ''
}

function Mensajes({ mensaje, error }) {
  return (
    <>
      {mensaje && <p className="mt-4 text-sm text-income">{mensaje}</p>}
      {error && <p role="alert" className="mt-4 text-sm text-expense">{error}</p>}
    </>
  )
}

export default function ChangePassword() {
  const [paso, setPaso] = useState(PASOS.correo)
  const [correo, setCorreo] = useState('')
  const [codigo, setCodigo] = useState('')
  const [nuevaClave, setNuevaClave] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  async function enviarCodigo(event) {
    event.preventDefault()
    setError('')
    try {
      await generarCodigoCambio(correo)
      setMensaje('El código fue enviado a tu correo electrónico.')
      setPaso(PASOS.codigo)
    } catch (exception) {
      setError(exception.message)
    }
  }

  function verificarCodigo(event) {
    event.preventDefault()
    setError(codigo.trim() ? '' : 'Escribe el código recibido.')
    if (codigo.trim()) setPaso(PASOS.clave)
  }

  async function guardarClave(event) {
    event.preventDefault()
    const errorClave = validarClave(nuevaClave, confirmacion)
    setError(errorClave)
    if (errorClave) return

    try {
      await cambiarClave(correo, codigo, nuevaClave, confirmacion)
      setMensaje('Contraseña actualizada. Ya puedes iniciar sesión con la nueva contraseña.')
      setPaso(PASOS.terminado)
    } catch (exception) {
      setError(exception.message)
    }
  }

  return (
    <Card className="p-8">
      <h1 className="text-xl font-bold">Cambiar contraseña</h1>
      <p className="mb-6 text-xs text-muted">Cambia la contraseña de tu cuenta.</p>

      {paso === PASOS.correo && (
        <form onSubmit={enviarCodigo} className="flex flex-col gap-4">
          <Input label="Correo electrónico" type="email" icon={Mail}
            placeholder="tucorreo@ejemplo.com" value={correo}
            onChange={(event) => setCorreo(event.target.value)} />
          <Button type="submit" size="lg" block>Enviar código</Button>
        </form>
      )}

      {paso === PASOS.codigo && (
        <form onSubmit={verificarCodigo} className="flex flex-col gap-4">
          <Input label="Código de 6 caracteres" type="text" icon={KeyRound}
            value={codigo} onChange={(event) => setCodigo(event.target.value.toUpperCase())}
            placeholder="ABC123" maxLength={6} />
          <Button type="submit" size="lg" block>Validar código</Button>
        </form>
      )}

      {paso === PASOS.clave && (
        <form onSubmit={guardarClave} className="flex flex-col gap-4">
          <Input label="Nueva contraseña" type="password" icon={LockKeyhole}
            value={nuevaClave} onChange={(event) => setNuevaClave(event.target.value)} />
          <Input label="Repite la contraseña" type="password" icon={LockKeyhole}
            value={confirmacion} onChange={(event) => setConfirmacion(event.target.value)} />
          <Button type="submit" size="lg" block>Guardar contraseña</Button>
        </form>
      )}

      <Mensajes mensaje={mensaje} error={error} />

      <p className="mt-6 text-center text-xs text-muted">
        ¿No tienes cuenta?{' '}
        <Link to={PATHS.registro} className="font-semibold text-primary">Regístrate</Link>
      </p>
      <p className="mt-6 text-center text-xs text-muted">
        ¿Te equivocaste?{' '}
        <Link to={PATHS.login} className="font-semibold text-primary">
          Regresa al inicio de sesión
        </Link>
      </p>
    </Card>
  )
}

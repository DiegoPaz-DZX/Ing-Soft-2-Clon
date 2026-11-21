import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Lock, Mail } from 'lucide-react'
import { Button, Card, Input } from '../../components/ui'
import { PATHS } from '../../routes/paths.js'
import { iniciarSesion } from '../../services/api.js'
import { guardarUsuario } from '../../services/sesion.js'

export default function Login() {
  const navigate = useNavigate()
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [error, setError] = useState('')
  const [enviando, setEnviando] = useState(false)

  async function enviar(e) {
    e.preventDefault()
    setError('')
    setEnviando(true)
    try {
      const usuario = await iniciarSesion(correo, contrasena)
      guardarUsuario(usuario)
      navigate(PATHS.dashboard)
    } catch (err) {
      setError(err.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <Card className="p-8">
      <h1 className="text-xl font-bold">Iniciar sesión</h1>
      <p className="mb-6 text-xs text-muted">Accede a tu cuenta Kyzen.</p>

      <form onSubmit={enviar} noValidate className="flex flex-col gap-4">
        <Input
          label="Correo electrónico"
          type="email"
          icon={Mail}
          placeholder="tucorreo@ejemplo.com"
          autoComplete="email"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
        />
        <Input
          label="Contraseña"
          type="password"
          icon={Lock}
          placeholder="••••••••"
          autoComplete="current-password"
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
        />

        {error && (
          <p className="rounded-xl border border-expense-soft bg-expense-soft/60 px-4 py-2.5 text-sm text-expense">
            {error}
          </p>
        )}

        <Button type="submit" size="lg" block disabled={enviando} className="mt-2">
          {enviando ? 'Ingresando…' : 'Ingresar'}
        </Button>
      </form>

      <p className="mt-6 text-center text-xs text-muted">
        ¿No tienes cuenta?{' '}
        <Link to={PATHS.registro} className="font-semibold text-primary">
          Regístrate
        </Link>
      </p>

      <p className="mt-6 text-center text-xs text-muted">
        ¿Olvidaste tu contraseña?{' '}
        <Link to={PATHS.changePassword} className="font-semibold text-primary">
          Cambia tu contraseña
        </Link>
      </p>
    </Card>
  )
}

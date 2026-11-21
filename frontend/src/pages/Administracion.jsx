import { useEffect, useState } from 'react'
import { Navigate } from 'react-router-dom'
import { Database, ShieldCheck } from 'lucide-react'

import { Card, CardTitle, PageContainer } from '../components/ui'
import { PATHS } from '../routes/paths.js'
import { cambiarRolUsuario, obtenerUsuariosAdmin } from '../services/api.js'
import { obtenerUsuario } from '../services/sesion.js'

export default function Administracion() {
  const sesion = obtenerUsuario()
  const [usuarios, setUsuarios] = useState([])
  const [cargando, setCargando] = useState(true)
  const [actualizando, setActualizando] = useState(null)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  useEffect(() => {
    if (sesion?.rol !== 'ADMINISTRADOR') return
    obtenerUsuariosAdmin(sesion.token)
      .then((respuesta) => setUsuarios(respuesta.usuarios))
      .catch((err) => setError(err.message))
      .finally(() => setCargando(false))
  }, [sesion?.rol, sesion?.token])

  if (sesion?.rol !== 'ADMINISTRADOR') {
    return <Navigate to={PATHS.dashboard} replace />
  }

  async function cambiarRol(cuentaId, rol) {
    setActualizando(cuentaId)
    setError('')
    setMensaje('')
    try {
      const actualizado = await cambiarRolUsuario(sesion.token, cuentaId, rol)
      setUsuarios((actuales) =>
        actuales.map((usuario) => usuario.id === actualizado.id ? actualizado : usuario),
      )
      setMensaje('Rol actualizado.')
    } catch (err) {
      setError(err.message)
    } finally {
      setActualizando(null)
    }
  }

  return (
    <PageContainer
      title="Administración"
      subtitle="Gestiona los permisos de las cuentas registradas."
    >
      <div className="grid gap-5 lg:grid-cols-[2fr_1fr]">
        <Card>
          <CardTitle>Roles de usuarios</CardTitle>
          {cargando && <p className="text-sm text-muted">Cargando usuarios...</p>}
          {error && <p role="alert" className="mb-3 text-sm text-expense">{error}</p>}
          {mensaje && <p className="mb-3 text-sm text-income">{mensaje}</p>}

          {!cargando && (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="border-b border-line text-xs uppercase text-muted">
                  <tr>
                    <th className="px-2 py-3 font-semibold">Correo</th>
                    <th className="px-2 py-3 font-semibold">Rol</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-line">
                  {usuarios.map((usuario) => (
                    <tr key={usuario.id}>
                      <td className="px-2 py-3">
                        <span className="font-medium">{usuario.correo}</span>
                        {usuario.id === sesion.id && (
                          <span className="ml-2 text-xs text-primary">Tu cuenta</span>
                        )}
                      </td>
                      <td className="px-2 py-3">
                        <select
                          value={usuario.rol}
                          disabled={actualizando === usuario.id}
                          onChange={(e) => cambiarRol(usuario.id, e.target.value)}
                          className="rounded-lg border border-line bg-white px-3 py-2 text-sm"
                        >
                          <option value="USUARIO">Usuario</option>
                          <option value="ADMINISTRADOR">Administrador</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Card>

        <div className="space-y-5">
          <Card tone="primary">
            <ShieldCheck className="mb-3 text-primary" size={28} />
            <h3 className="font-semibold">Acceso protegido</h3>
            <p className="mt-2 text-sm text-muted">
              Solo una sesión con rol de administrador puede consultar o cambiar roles.
            </p>
          </Card>
          <Card>
            <Database className="mb-3 text-income" size={28} />
            <h3 className="font-semibold">Datos cifrados</h3>
            <p className="mt-2 text-sm text-muted">
              Las descripciones se cifran antes de guardarse en SQLite. El acceso a los datos
              se controla mediante los permisos de la aplicación.
            </p>
          </Card>
        </div>
      </div>
    </PageContainer>
  )
}

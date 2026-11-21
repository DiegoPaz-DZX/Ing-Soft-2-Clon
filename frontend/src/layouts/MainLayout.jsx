import { Navigate, Outlet, useLocation } from 'react-router-dom'
import Navbar from '../components/layout/Navbar.jsx'
import { PATHS } from '../routes/paths.js'
import { obtenerUsuario } from '../services/sesion.js'
import { MonedaProvider } from '../context/MonedaContext.jsx'

const rutas = [PATHS.metas, PATHS.exportar, PATHS.administracion]

export default function MainLayout() {
  if (!obtenerUsuario()) {
    return <Navigate to={PATHS.login} replace />
  }
  const location = useLocation()

  const esPaginaCompleta = rutas.includes(location.pathname)

  const anchoPrincipal = esPaginaCompleta ? 'max-w-7xl' : 'max-w-5xl'

  return (
    <MonedaProvider>
      <div className="min-h-screen bg-app">
        <Navbar />
        <main className={`mx-auto w-full ${anchoPrincipal} px-4 py-8 sm:px-6 lg:py-10`}>
          <Outlet />
        </main>
      </div>
    </MonedaProvider>
  )
}

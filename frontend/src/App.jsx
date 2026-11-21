import { Route, Routes } from 'react-router-dom'
import MainLayout from './layouts/MainLayout.jsx'
import AuthLayout from './layouts/AuthLayout.jsx'
import { PATHS } from './routes/paths.js'
import Dashboard from './pages/Dashboard.jsx'
import Transacciones from './pages/Transacciones.jsx'
import Historial from './pages/Historial.jsx'
import Reportes from './pages/Reportes.jsx'
import Consultoria from './pages/Consultoria.jsx'
import ExportarReporte from './pages/ExportarReporte.jsx'
import ReporteFinanciero from './pages/ReporteFinanciero.jsx'
import Metas from './pages/Metas.jsx'
import Alertas from './pages/Alertas.jsx'
import MonitorSalud from './pages/MonitorSalud.jsx'
import Perfil from './pages/Perfil.jsx'
import Login from './pages/auth/Login.jsx'
import Registro from './pages/auth/Registro.jsx'
import NotFound from './pages/NotFound.jsx'
import ChangePassword from './pages/auth/ChangePassword.jsx'
import Administracion from './pages/Administracion.jsx'

export default function App() {
  return (
    <Routes>
      <Route element={<AuthLayout />}>
        <Route path={PATHS.login} element={<Login />} />
        <Route path={PATHS.registro} element={<Registro />} />
        <Route path={PATHS.changePassword} element={<ChangePassword />} />
      </Route>

      <Route element={<MainLayout />}>
        <Route path={PATHS.dashboard} element={<Dashboard />} />
        <Route path={PATHS.transacciones} element={<Transacciones />} />
        <Route path={PATHS.historial} element={<Historial />} />
        <Route path={PATHS.reportes} element={<Reportes />} />
        <Route path={PATHS.exportar} element={<ExportarReporte />} />
        <Route path={PATHS.reporteFinanciero} element={<ReporteFinanciero />} />
        <Route path={PATHS.consultoria} element={<Consultoria />} />
        <Route path={PATHS.metas} element={<Metas />} />
        <Route path={PATHS.alertas} element={<Alertas />} />
        <Route path={PATHS.monitor} element={<MonitorSalud />} />
        <Route path={PATHS.perfil} element={<Perfil />} />
        <Route path={PATHS.administracion} element={<Administracion />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

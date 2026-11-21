import {
  Activity,
  ArrowLeftRight,
  Bell,
  BarChart3,
  Home,
  ScrollText,
  ShieldCheck,
  Target,
  User,
} from 'lucide-react'

export const PATHS = {
  login: '/login',
  registro: '/registro',
  dashboard: '/',
  transacciones: '/transacciones',
  historial: '/historial',
  reportes: '/reportes',
  consultoria: '/consultoria',
  exportar: '/reportes/exportar',
  reporteFinanciero: '/reportes/financiero',
  metas: '/metas',
  alertas: '/alertas',
  monitor: '/monitor',
  perfil: '/perfil',
  changePassword: '/change-password',
  administracion: '/administracion',
}

// Orden y etiquetas de la barra de navegación principal (según los mockups)
export const NAV_ITEMS = [
  { to: PATHS.dashboard, label: 'Panel principal', icon: Home, end: true },
  { to: PATHS.transacciones, label: 'Transacciones', icon: ArrowLeftRight },
  { to: PATHS.historial, label: 'Historial de movimientos', icon: ScrollText },
  { to: PATHS.reportes, label: 'Reportes analíticos', icon: BarChart3 },
  { to: PATHS.metas, label: 'Objetivos de ahorro', icon: Target },
  { to: PATHS.alertas, label: 'Alertas', icon: Bell },
  { to: PATHS.monitor, label: 'Monitor de salud', icon: Activity },
  { to: PATHS.perfil, label: 'Mi perfil', icon: User },
]

export const ADMIN_NAV_ITEM = {
  to: PATHS.administracion,
  label: 'Administración',
  icon: ShieldCheck,
}

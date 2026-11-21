import { useState } from 'react'
import {Link, NavLink, useNavigate} from 'react-router-dom'
import { Bell, LogOut, Menu, X } from 'lucide-react'
import Logo from './Logo.jsx'
import { ADMIN_NAV_ITEM, NAV_ITEMS, PATHS } from '../../routes/paths.js'
import { obtenerUsuario, cerrarSesionRemota } from '../../services/sesion.js'
import { useMoneda } from '../../context/MonedaContext.jsx'

function navClass({ isActive }) {
  const base =
    'flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[11px] font-semibold uppercase tracking-wide transition-colors'
  return isActive
    ? `${base} bg-income-soft text-income`
    : `${base} text-muted hover:bg-app hover:text-ink`
}

export default function Navbar() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const usuario = obtenerUsuario()
  const { divisa } = useMoneda()
  const items = usuario?.rol === 'ADMINISTRADOR' ? [...NAV_ITEMS, ADMIN_NAV_ITEM] : NAV_ITEMS

  async function logout() {
    try {
      await cerrarSesionRemota()
    } finally {
      navigate(PATHS.login, { replace: true })
    }
  }

  return (
    <header className="sticky top-0 z-30 border-b border-line bg-surface/90 backdrop-blur">
      <div className="mx-auto flex h-16 w-full max-w-7xl items-center gap-4 px-4 sm:px-6">
        <Link to={PATHS.dashboard} className="shrink-0">
          <Logo />
        </Link>

        <nav className="hidden flex-1 items-center justify-center gap-1 xl:flex">
          {items.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end} className={navClass}>
              <Icon size={14} strokeWidth={2.2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3 xl:ml-0">
          <button
            type="button"
            className="rounded-full p-2 text-ink hover:bg-app"
            aria-label="Notificaciones"
          >
            <Bell size={18} />
          </button>

          <Link
            to={PATHS.perfil}
            title={`Divisa base: ${divisa.nombre}`}
            className="rounded-full border border-line px-2.5 py-1 text-[10px] font-semibold tracking-wide text-muted hover:border-primary hover:text-primary"
          >
            {divisa.simbolo} {divisa.codigo}
          </Link>

          <div className="hidden text-right leading-tight sm:block">
            <p className="text-sm font-semibold">{usuario?.correo ?? 'Invitado'}</p>
            <p className="text-[10px] font-medium tracking-wide text-primary uppercase">
              {usuario?.rol === 'ADMINISTRADOR' ? 'Administrador' : 'Usuario'}
            </p>
          </div>

          <button
            onClick={logout}
            type="button"
            className="hidden rounded-full p-2 text-muted hover:bg-app hover:text-ink sm:block hover:cursor-pointer hover:text-black"
            aria-label="Cerrar sesión"
          >
            <LogOut size={16} />
          </button>

          <button
            type="button"
            className="rounded-full p-2 text-ink hover:bg-app xl:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Abrir menú"
            aria-expanded={open}
          >
            {open ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {open && (
        <nav className="border-t border-line bg-surface px-4 py-3 xl:hidden">
          <ul className="flex flex-col gap-1">
            {items.map(({ to, label, icon: Icon, end }) => (
              <li key={to}>
                <NavLink
                  to={to}
                  end={end}
                  className={navClass}
                  onClick={() => setOpen(false)}
                >
                  <Icon size={14} strokeWidth={2.2} />
                  {label}
                </NavLink>
              </li>
            ))}
            <li>
              <button
                type="button"
                className="flex w-full items-center gap-1.5 rounded-full px-3 py-1.5 text-left text-[11px] font-semibold uppercase tracking-wide text-muted hover:bg-app hover:text-ink"
                onClick={logout}
              >
                <LogOut size={14} />
                Cerrar sesión
              </button>
            </li>
          </ul>
        </nav>
      )}
    </header>
  )
}

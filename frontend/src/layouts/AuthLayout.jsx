import { Outlet } from 'react-router-dom'
import Logo from '../components/layout/Logo.jsx'

export default function AuthLayout() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-app px-4 py-10">
      <div className="mb-8 flex items-center gap-3">
        <Logo size="lg" />
        <span className="text-2xl font-bold tracking-tight">Kyzen</span>
      </div>
      <div className="w-full max-w-md">
        <Outlet />
      </div>
    </div>
  )
}

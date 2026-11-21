import { useEffect, useState } from 'react'
import { Card, CardTitle, PageContainer } from '../components/ui'
import AlertaSobregasto from '../components/AlertaSobregasto'
import GestorLimites from '../components/GestorLimites'
import { ServicioAlertas } from '../services/ServicioAlertas'

export default function Alertas() {
  const [alertas, setAlertas] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const cargar = async () => {
      const alertasObtenidas = await ServicioAlertas.obtenerAlertas()
      setAlertas(alertasObtenidas)
      setCargando(false)
    }
    cargar()
    const intervalo = setInterval(cargar, 10000)
    return () => clearInterval(intervalo)
  }, [])

  return (
    <PageContainer title="Alertas de Sobregasto" subtitle="Monitorea tus límites de gasto.">
      <div className="grid gap-5 md:grid-cols-3">
        <div className="md:col-span-2">
          <Card>
            <CardTitle>Alertas Activas</CardTitle>
            {cargando ? (
              <p className="mt-4 text-sm text-gray-500">Cargando...</p>
            ) : alertas.length === 0 ? (
              <p className="mt-4 text-sm text-gray-500">No hay alertas. ¡Vas bien! 🎉</p>
            ) : (
              <div className="mt-4 space-y-3">
                {alertas.map((alerta, i) => (
                  <AlertaSobregasto key={i} alerta={alerta} onCerrar={() => setAlertas(alertas.filter((_, idx) => idx !== i))} />
                ))}
              </div>
            )}
          </Card>
        </div>
        <GestorLimites />
      </div>
    </PageContainer>
  )
}
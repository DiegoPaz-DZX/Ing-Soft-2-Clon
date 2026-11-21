import { Card, CardTitle, PageContainer, Placeholder } from '../components/ui'
import TarjetaBalance from '../components/TarjetaBalance.jsx'
import TipsEducativos from '../components/TipsEducativos.jsx'
import ListaRecomendaciones from '../components/ListaRecomendaciones.jsx' // NUEVO
import MonitorProyeccion from '../components/MonitorProyeccion.jsx'

export default function Dashboard() {
  return (
    <PageContainer title="¡Bienvenido! 👋" subtitle="Estado actual de tus finanzas personales.">
      <Card tone="primary" className="mb-5">
        <CardTitle>Balance general</CardTitle>
        <TarjetaBalance />
      </Card>

      <Card className="mb-5">
        <CardTitle>Proyección de gasto</CardTitle>
        <MonitorProyeccion />
      </Card>

      <div className="grid gap-5 md:grid-cols-2">
        <Card>
          <CardTitle>Distribución por categoría</CardTitle>
          <Placeholder className="min-h-56" />
        </Card>
        <Card>
          <CardTitle>Gastos mensuales</CardTitle>
          <Placeholder className="min-h-56" />
        </Card>
      </div>

      {/* NUEVO: recomendaciones basadas en los patrones de gasto */}
      <Card className="mt-5">
        <CardTitle>Recomendaciones para ti</CardTitle>
        <ListaRecomendaciones />
      </Card>

      <Card className="mt-5">
        <CardTitle>Tips educativos</CardTitle>
        <TipsEducativos />
      </Card>
    </PageContainer>
  )
}
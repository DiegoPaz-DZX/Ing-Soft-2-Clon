import { Link } from 'react-router-dom'
import { Sparkles } from 'lucide-react'
import { Button, Card, CardTitle, PageContainer, Placeholder } from '../components/ui'
import { PATHS } from '../routes/paths.js'

export default function Consultoria() {
  return (
    <div>
      <p className="mb-1 flex items-center gap-1.5 text-[10px] font-semibold tracking-wider text-primary uppercase">
        <Sparkles size={12} /> Módulo de inteligencia artificial
      </p>
      <PageContainer
        title="Centro de Consultoría Financiera"
        actions={
          <Link to={PATHS.reportes}>
            <Button variant="outline" size="sm">
              Volver al panel
            </Button>
          </Link>
        }
      >
        <div className="mb-5 grid gap-5 md:grid-cols-3">
          <Card>
            <CardTitle>Diagnóstico predictivo</CardTitle>
            <Placeholder className="min-h-40" />
          </Card>
          <Card className="md:col-span-2">
            <CardTitle>Métricas de control de riesgo</CardTitle>
            <Placeholder className="min-h-40" />
          </Card>
        </div>

        <Card>
          <CardTitle>Asesoría en tiempo real</CardTitle>
          <Placeholder className="min-h-40" />
        </Card>
      </PageContainer>
    </div>
  )
}

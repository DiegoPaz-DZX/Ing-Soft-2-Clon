import { Card, CardTitle, PageContainer, Placeholder } from '../components/ui'
import PreferenciaMoneda from '../components/PreferenciaMoneda.jsx'

export default function Perfil() {
  return (
    <PageContainer title="Mi perfil" subtitle="Tu cuenta y preferencias.">
      <div className="grid gap-5 md:grid-cols-2">
        <Card>
          <CardTitle>Datos de la cuenta</CardTitle>
          <Placeholder className="min-h-40" />
        </Card>
        <Card>
          <CardTitle>Preferencias de moneda</CardTitle>
          <PreferenciaMoneda />
        </Card>
      </div>
    </PageContainer>
  )
}

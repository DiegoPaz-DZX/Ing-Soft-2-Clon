import { Link } from 'react-router-dom'
import { Button, PageContainer } from '../components/ui'
import { PATHS } from '../routes/paths.js'

export default function NotFound() {
  return (
    <PageContainer title="Página no encontrada" subtitle="La ruta que buscas no existe.">
      <Link to={PATHS.dashboard}>
        <Button>Ir al panel principal</Button>
      </Link>
    </PageContainer>
  )
}

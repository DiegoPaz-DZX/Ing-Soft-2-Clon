import { Modal } from '../ui'
import { urlDjango } from '../../services/api.js'

export default function VisorComprobante({ comprobante, onClose }) {
  const url = urlDjango(comprobante?.url)

  return (
    <Modal open={Boolean(comprobante)} onClose={onClose} title="Comprobante" subtitle={comprobante?.nombre}>
      {!url && (
        <p className="text-xs text-muted">
          El comprobante aún no está disponible. Se mostrará cuando el servidor lo reciba.
        </p>
      )}
      {url && comprobante.tipo === 'application/pdf' && (
        <iframe src={url} title="Comprobante PDF" className="h-[60vh] w-full rounded-xl" />
      )}
      {url && comprobante.tipo !== 'application/pdf' && (
        <img src={url} alt="Comprobante" className="w-full rounded-xl" />
      )}
    </Modal>
  )
}
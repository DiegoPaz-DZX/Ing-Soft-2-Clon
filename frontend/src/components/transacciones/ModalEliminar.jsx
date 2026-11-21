import { Button, Modal } from '../ui'

export default function ModalEliminar({ open, detalle, eliminando, error, onConfirmar, onCancelar }) {
  return (
    <Modal
      open={open}
      onClose={eliminando ? undefined : onCancelar}
      title="Eliminar transacción"
      subtitle="Esta acción no se puede deshacer."
      footer={
        <div className="flex justify-end gap-2">
          <Button variant="outline" onClick={onCancelar} disabled={eliminando}>
            Cancelar
          </Button>
          <Button variant="dark" onClick={onConfirmar} disabled={eliminando}>
            {eliminando ? 'Eliminando…' : 'Eliminar'}
          </Button>
        </div>
      }
    >
      <p className="text-sm text-ink">¿Seguro que quieres eliminar este movimiento?</p>
      <p className="mt-2 rounded-xl border border-line bg-app px-3 py-2 text-sm font-medium">
        {detalle}
      </p>
      {error && (
        <p role="alert" className="mt-3 rounded-xl bg-expense-soft px-3 py-2 text-xs text-expense">
          {error}
        </p>
      )}
    </Modal>
  )
}
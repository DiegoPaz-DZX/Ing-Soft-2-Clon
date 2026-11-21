// Espacio vacío reservado para el contenido de cada sección
export default function Placeholder({ className = '' }) {
  return (
    <div
      className={`min-h-28 rounded-2xl border-2 border-dashed border-line bg-app/60 ${className}`}
    />
  )
}
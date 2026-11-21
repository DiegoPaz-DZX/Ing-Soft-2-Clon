export default function BarraMeta({ nombre, progreso, formatear }) {
  const { porcentaje, ahorradoPEN, objetivoPEN, faltantePEN, completada } = progreso

  return (
    <div className="mt-4">
      <div className="mb-2 flex items-center justify-between text-sm">
        <span className="font-semibold">{nombre}</span>
        <span className="font-bold text-primary">{porcentaje.toFixed(0)}%</span>
      </div>
      <div
        className="h-4 w-full overflow-hidden rounded-full bg-gray-200"
        role="progressbar"
        aria-label={`Progreso de ${nombre}`}
        aria-valuenow={porcentaje}
        aria-valuemin="0"
        aria-valuemax="100"
      >
        <div
          className="h-full rounded-full bg-primary transition-all duration-500"
          style={{ width: `${porcentaje}%` }}
        />
      </div>
      <div className="mt-2 flex justify-between text-xs text-muted">
        <span>{formatear(ahorradoPEN)} ahorrados</span>
        <span>{formatear(objetivoPEN)} objetivo</span>
      </div>
      {completada ? (
        <p className="mt-2 text-xs font-semibold text-income">Meta completada</p>
      ) : (
        <p className="mt-2 text-xs text-muted">Faltan {formatear(faltantePEN)}</p>
      )}
    </div>
  )
}

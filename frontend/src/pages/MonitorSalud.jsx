import { useEffect, useState } from 'react'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Tooltip, Legend } from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { Card, CardTitle, PageContainer } from '../components/ui'
import { obtenerMonitorSalud } from '../services/api.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const ESTADOS = {
  saludable: {
    etiqueta: 'Saludable',
    clases: 'border-emerald-200 bg-emerald-50 text-emerald-800',
    color: '#10b981',
  },
  atencion: {
    etiqueta: 'Atención',
    clases: 'border-amber-200 bg-amber-50 text-amber-800',
    color: '#f59e0b',
  },
  critico: {
    etiqueta: 'Crítico',
    clases: 'border-red-200 bg-red-50 text-red-800',
    color: '#ef4444',
  },
}

function formatearSoles(valor) {
  return `S/ ${Number(valor).toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function formatearPorcentaje(valor) {
  return valor === null || valor === undefined ? 'Sin datos' : `${valor.toFixed(1)}%`
}

const OPCIONES_GRAFICO = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { position: 'bottom' } },
}

export default function MonitorSalud() {
  const [datos, setDatos] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    obtenerMonitorSalud()
      .then(setDatos)
      .catch((e) => setError(e.message || 'No se pudo cargar el monitor'))
  }, [])

  const subtitulo = 'Evalúa tus desviaciones contables mes a mes.'

  if (error) {
    return (
      <PageContainer title="Monitor de salud" subtitle={subtitulo}>
        <Card>
          <p className="text-sm text-red-600">{error}</p>
        </Card>
      </PageContainer>
    )
  }

  if (!datos) {
    return (
      <PageContainer title="Monitor de salud" subtitle={subtitulo}>
        <Card>
          <p className="text-sm text-gray-500">Cargando…</p>
        </Card>
      </PageContainer>
    )
  }

  if (datos.meses.length === 0) {
    return (
      <PageContainer title="Monitor de salud" subtitle={subtitulo}>
        <Card>
          <p className="text-sm text-gray-500">
            Aún no tienes movimientos para evaluar. Registra transacciones para ver tu monitor.
          </p>
        </Card>
      </PageContainer>
    )
  }

  const meses = datos.meses
  const actual = datos.estado_actual
  const estadoActual = ESTADOS[actual.estado]
  const etiquetas = meses.map((m) => m.etiqueta)

  const datosFlujo = {
    labels: etiquetas,
    datasets: [
      { label: 'Ingresos', data: meses.map((m) => m.ingresos), backgroundColor: '#10b981' },
      { label: 'Gastos', data: meses.map((m) => m.gastos), backgroundColor: '#ef4444' },
    ],
  }

  const datosDesviacion = {
    labels: etiquetas,
    datasets: [
      {
        label: 'Desviación del gasto (%)',
        data: meses.map((m) => m.desviacion_gasto),
        backgroundColor: meses.map((m) => ESTADOS[m.estado].color),
      },
    ],
  }

  return (
    <PageContainer title="Monitor de salud" subtitle={subtitulo}>
      <div className="grid gap-5 md:grid-cols-4">
        <div className={`rounded-lg border p-4 md:col-span-2 ${estadoActual.clases}`}>
          <p className="text-xs uppercase tracking-wide">Estado de {actual.etiqueta}</p>
          <p className="mt-1 text-2xl font-bold">{estadoActual.etiqueta}</p>
        </div>
        <Card>
          <CardTitle>Tasa de ahorro</CardTitle>
          <p className="mt-2 text-xl font-semibold">{formatearPorcentaje(actual.tasa_ahorro)}</p>
        </Card>
        <Card>
          <CardTitle>Desviación del gasto</CardTitle>
          <p className="mt-2 text-xl font-semibold">
            {formatearPorcentaje(actual.desviacion_gasto)}
          </p>
        </Card>
      </div>

      <div className="mt-5 grid gap-5 md:grid-cols-2">
        <Card>
          <CardTitle>Ingresos vs gastos por mes</CardTitle>
          <div className="mt-4 h-72">
            <Bar data={datosFlujo} options={OPCIONES_GRAFICO} />
          </div>
        </Card>
        <Card>
          <CardTitle>Desviación del gasto frente al promedio previo</CardTitle>
          <div className="mt-4 h-72">
            <Bar data={datosDesviacion} options={OPCIONES_GRAFICO} />
          </div>
        </Card>
      </div>

      <div className="mt-5">
        <Card>
          <CardTitle>Resumen de meses evaluados</CardTitle>
          <ul className="mt-4 divide-y divide-gray-200 text-sm">
            {meses.map((m) => (
              <li key={m.periodo} className="flex items-center justify-between py-2">
                <span>{m.etiqueta}</span>
                <span className="text-gray-600">
                  Balance {formatearSoles(m.balance)} · Desviación{' '}
                  {formatearPorcentaje(m.desviacion_gasto)}
                </span>
                <span className={`rounded-full border px-2 py-0.5 text-xs ${ESTADOS[m.estado].clases}`}>
                  {ESTADOS[m.estado].etiqueta}
                </span>
              </li>
            ))}
          </ul>
          <p className="mt-4 text-xs text-gray-500">
            Saludables: {datos.resumen.saludables} · Atención: {datos.resumen.atencion} · Críticos:{' '}
            {datos.resumen.criticos}
          </p>
        </Card>
      </div>
    </PageContainer>
  )
}
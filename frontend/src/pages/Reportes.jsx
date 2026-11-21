import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { FileDown, FileText, Sparkles } from 'lucide-react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'

import { Button, Card, CardTitle, PageContainer, Tabs } from '../components/ui'
import { PATHS } from '../routes/paths.js'
import { useTransacciones } from '../context/TransaccionesContext'
import { buscarCategoria } from '../domain/categorias'
import { obtenerReporteFinanciero } from '../services/api.js'

// Registramos los elementos que utilizará Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
)

const PERIODOS = [
  { value: 'mensual', label: 'Mensual' },
  { value: 'semanal', label: 'Semanal' },
  { value: 'anual', label: 'Anual' },
]

function formatearMoneda(valor) {
  return `S/ ${Number(valor).toLocaleString('es-PE', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`
}

function obtenerNombreMes(numeroMes) {
  const meses = [
    'Enero',
    'Febrero',
    'Marzo',
    'Abril',
    'Mayo',
    'Junio',
    'Julio',
    'Agosto',
    'Septiembre',
    'Octubre',
    'Noviembre',
    'Diciembre',
  ]

  return meses[numeroMes]
}

function agruparPorPeriodo(transacciones, periodo) {
  const grupos = {}

  transacciones.forEach((transaccion) => {
    const fecha = new Date(`${transaccion.fecha}T00:00:00`)
    const clave = periodo === 'mensual'
      ? `${fecha.getFullYear()}-${fecha.getMonth()}`
      : periodo === 'anual'
        ? `${fecha.getFullYear()}`
        : transaccion.fecha
    const etiqueta = periodo === 'mensual'
      ? `${obtenerNombreMes(fecha.getMonth())} ${fecha.getFullYear()}`
      : periodo === 'anual'
        ? `${fecha.getFullYear()}`
        : fecha.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit' })

    grupos[clave] ??= { etiqueta, ingresos: 0, gastos: 0 }
    if (transaccion.tipo === 'ingreso') grupos[clave].ingresos += Number(transaccion.monto)
    if (transaccion.tipo === 'gasto') grupos[clave].gastos += Number(transaccion.monto)
  })

  return Object.entries(grupos)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([, valor]) => valor)
}

function agruparGastosPorCategoria(transacciones) {
  return transacciones.reduce((grupos, transaccion) => {
    if (transaccion.tipo !== 'gasto') return grupos
    const categoria = buscarCategoria(transaccion.categoria)
    const nombre = categoria?.nombre ?? 'Otros'
    grupos[nombre] = (grupos[nombre] ?? 0) + Number(transaccion.monto)
    return grupos
  }, {})
}

export default function Reportes() {
  const [periodo, setPeriodo] = useState('mensual')
  const [reporte, setReporte] = useState(null)
  const [error, setError] = useState('')

  const { transacciones } = useTransacciones()

  useEffect(() => {
    let activo = true
    obtenerReporteFinanciero({ graficos: true, analisis: true })
      .then((datos) => {
        if (activo) {
          setReporte(datos)
          setError('')
        }
      })
      .catch((exception) => {
        if (activo) setError(exception.message)
      })
    return () => {
      activo = false
    }
  }, [])

  const transaccionesFuente = reporte
    ? reporte.movimientos.map((movimiento) => ({
        ...movimiento,
        tipo: movimiento.tipo.toLowerCase(),
        monto: movimiento.montoEnSoles,
      }))
    : transacciones

  const datosPeriodo = useMemo(() => {
    return agruparPorPeriodo(transaccionesFuente, periodo)
  }, [transaccionesFuente, periodo])

  const totalIngresos = useMemo(() => {
    return datosPeriodo.reduce(
      (total, item) => total + item.ingresos,
      0,
    )
  }, [datosPeriodo])

  const totalGastos = useMemo(() => {
    return datosPeriodo.reduce(
      (total, item) => total + item.gastos,
      0,
    )
  }, [datosPeriodo])

  const gastosPorCategoria = useMemo(() => {
    return agruparGastosPorCategoria(transaccionesFuente)
  }, [transaccionesFuente])

  const datosBarras = {
    labels: datosPeriodo.map((item) => item.etiqueta),

    datasets: [
      {
        label: 'Ingresos',
        data: datosPeriodo.map((item) => item.ingresos),
        backgroundColor: '#16a34a',
        borderRadius: 6,
      },
      {
        label: 'Gastos',
        data: datosPeriodo.map((item) => item.gastos),
        backgroundColor: '#dc2626',
        borderRadius: 6,
      },
    ],
  }

  const datosDoughnut = {
    labels: Object.keys(gastosPorCategoria),

    datasets: [
      {
        data: Object.values(gastosPorCategoria),

        backgroundColor: [
          '#f97316',
          '#0ea5e9',
          '#8b5cf6',
          '#ec4899',
          '#10b981',
          '#f59e0b',
          '#64748b',
        ],

        borderWidth: 1,
      },
    ],
  }

  const opcionesBarras = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: 'top',
      },

      title: {
        display: false,
      },

      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.dataset.label}: ${formatearMoneda(
              context.raw,
            )}`
          },
        },
      },
    },

    scales: {
      y: {
        beginAtZero: true,

        ticks: {
          callback: function (value) {
            return `S/ ${value}`
          },
        },
      },
    },
  }

  const opcionesDoughnut = {
    responsive: true,
    maintainAspectRatio: false,

    plugins: {
      legend: {
        position: 'bottom',
      },

      tooltip: {
        callbacks: {
          label: function (context) {
            return `${context.label}: ${formatearMoneda(
              context.raw,
            )}`
          },
        },
      },
    },
  }

  const hayDatos = transacciones.length > 0

  return (
    <PageContainer
      title="Reportes Analíticos"
      subtitle="Control financiero de tus finanzas por periodo."
      backTo={PATHS.dashboard}
      actions={
        <>
          <Link to={PATHS.consultoria}>
            <Button variant="outline" size="sm">
              <Sparkles size={14} /> IA
            </Button>
          </Link>

          <Link to={PATHS.reporteFinanciero}>
            <Button variant="outline" size="sm">
              <FileText size={14} /> Reporte financiero
            </Button>
          </Link>

          <Link to={PATHS.exportar}>
            <Button variant="solid" size="sm" className="hover:scale-105 hover:cursor-pointer">
              <FileDown size={14} /> Exportar
            </Button>
          </Link>
        </>
      }
    >
      <div className="mb-6 flex justify-center">
        <Tabs
          options={PERIODOS}
          value={periodo}
          onChange={setPeriodo}
        />
      </div>

      {error && (
        <p role="alert" className="mb-4 rounded-xl border border-expense-soft bg-expense-soft/60 px-4 py-2.5 text-sm text-expense">
          {error}
        </p>
      )}

      {!reporte && !error && (
        <p className="mb-5 rounded-2xl bg-app py-8 text-center text-sm text-muted">
          Cargando movimientos del servidor…
        </p>
      )}

      <div className="mb-5 grid gap-5 sm:grid-cols-2">
        <Card>
          <CardTitle className="text-income">
            Ingresos del periodo
          </CardTitle>

          <p className="mt-3 text-2xl font-bold text-income">
            {formatearMoneda(totalIngresos)}
          </p>
        </Card>

        <Card>
          <CardTitle className="text-expense">
            Gastos del periodo
          </CardTitle>

          <p className="mt-3 text-2xl font-bold text-expense">
            {formatearMoneda(totalGastos)}
          </p>
        </Card>
      </div>

      <Card className="mb-5">
        <CardTitle>Ingresos vs gastos</CardTitle>

        {!hayDatos ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-muted">
            No hay datos para mostrar.
          </div>
        ) : (
          <div className="mt-4 h-72">
            <Bar
              data={datosBarras}
              options={opcionesBarras}
            />
          </div>
        )}
      </Card>

      <Card>
        <CardTitle>
          Distribución de gastos por categoría
        </CardTitle>

        {!hayDatos ||
        Object.keys(gastosPorCategoria).length === 0 ? (
          <div className="flex min-h-64 items-center justify-center text-sm text-muted">
            No hay gastos registrados para mostrar.
          </div>
        ) : (
          <div className="mx-auto mt-4 h-72 max-w-xl">
            <Doughnut
              data={datosDoughnut}
              options={opcionesDoughnut}
            />
          </div>
        )}
      </Card>
    </PageContainer>
  )
}

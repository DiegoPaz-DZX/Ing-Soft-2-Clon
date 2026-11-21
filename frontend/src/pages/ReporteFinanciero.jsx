import { useEffect, useState } from 'react'
import { CalendarDays, FileDown, FileSpreadsheet } from 'lucide-react'
import {
  ArcElement,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar, Doughnut } from 'react-chartjs-2'

import { Badge, Button, Card, CardTitle, Input, PageContainer } from '../components/ui'
import { PATHS } from '../routes/paths.js'
import { descargarReporteFinanciero, obtenerReporteFinanciero } from '../services/api.js'
import { useMoneda } from '../context/MonedaContext.jsx'

ChartJS.register(CategoryScale, LinearScale, BarElement, ArcElement, Tooltip, Legend)

const COLORES_CATEGORIAS = ['#f97316', '#0ea5e9', '#8b5cf6', '#ec4899', '#10b981', '#f59e0b', '#64748b']
const TONOS = { advertencia: 'expense', positivo: 'income', informacion: 'primary' }
const ETIQUETAS_NIVEL = { advertencia: 'Atención', positivo: 'Bien', informacion: 'Dato' }

function formatearFecha(iso) {
  const [anio, mes, dia] = iso.split('-')
  return `${dia}/${mes}/${anio}`
}

function describirPeriodo(reporte) {
  if (!reporte.desde || !reporte.hasta) return 'Todos los movimientos registrados'
  return `Del ${formatearFecha(reporte.desde)} al ${formatearFecha(reporte.hasta)}`
}

export default function ReporteFinanciero() {
  const { divisa, convertir, formatear } = useMoneda()
  const [desde, setDesde] = useState('')
  const [hasta, setHasta] = useState('')
  const [graficos, setGraficos] = useState(true)
  const [analisis, setAnalisis] = useState(true)
  const [opciones, setOpciones] = useState({ graficos: true, analisis: true })
  const [reporte, setReporte] = useState(null)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [descargando, setDescargando] = useState('')

  async function generar(nuevasOpciones) {
    setCargando(true)
    setError('')
    try {
      setReporte(await obtenerReporteFinanciero(nuevasOpciones))
      setOpciones(nuevasOpciones)
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  useEffect(() => {
    generar({ graficos: true, analisis: true })
  }, [])

  function enviar(e) {
    e.preventDefault()
    generar({ desde, hasta, graficos, analisis })
  }

  async function descargar(formato) {
    setDescargando(formato)
    setError('')
    try {
      await descargarReporteFinanciero({ ...opciones, desde: reporte.desde, hasta: reporte.hasta }, formato)
    } catch (e) {
      setError(e.message)
    } finally {
      setDescargando('')
    }
  }

  const hayMovimientos = reporte && reporte.cantidadMovimientos > 0

  const datosBarras = reporte && {
    labels: reporte.evolucionMensual.map((mes) => mes.etiqueta),
    datasets: [
      {
        label: 'Ingresos',
        data: reporte.evolucionMensual.map((mes) => convertir(mes.ingresos)),
        backgroundColor: '#16a34a',
        borderRadius: 6,
      },
      {
        label: 'Gastos',
        data: reporte.evolucionMensual.map((mes) => convertir(mes.gastos)),
        backgroundColor: '#dc2626',
        borderRadius: 6,
      },
    ],
  }

  const datosCategorias = reporte && {
    labels: reporte.gastosPorCategoria.map((categoria) => categoria.nombre),
    datasets: [
      {
        data: reporte.gastosPorCategoria.map((categoria) => convertir(categoria.monto)),
        backgroundColor: COLORES_CATEGORIAS,
        borderWidth: 1,
      },
    ],
  }

  const etiquetaMonto = (valor) =>
    `${divisa.simbolo} ${Number(valor).toLocaleString('es-PE', { maximumFractionDigits: 2 })}`

  const opcionesBarras = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { position: 'top' },
      tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${etiquetaMonto(ctx.raw)}` } },
    },
    scales: { y: { beginAtZero: true, ticks: { callback: (valor) => etiquetaMonto(valor) } } },
  }

  const opcionesCategorias = {
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: { position: 'bottom' },
      tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${etiquetaMonto(ctx.raw)}` } },
    },
  }

  return (
    <PageContainer
      title="Reporte financiero"
      subtitle="Genera, revisa y exporta el análisis de tus finanzas."
      backTo={PATHS.reportes}
      actions={
        <div className="flex flex-wrap gap-2">
          <Button
            variant="solid"
            size="sm"
            onClick={() => descargar('pdf')}
            disabled={!hayMovimientos || Boolean(descargando)}
          >
            <FileDown size={14} /> {descargando === 'pdf' ? 'Generando…' : 'Descargar PDF'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => descargar('csv')}
            disabled={!hayMovimientos || Boolean(descargando)}
          >
            <FileSpreadsheet size={14} /> {descargando === 'csv' ? 'Generando…' : 'Descargar CSV'}
          </Button>
        </div>
      }
    >
      <form
        onSubmit={enviar}
        className="mb-5 rounded-2xl border border-line bg-app/60 p-4"
      >
        <div className="flex flex-wrap items-end gap-3">
          <Input
            label="Desde"
            type="date"
            icon={CalendarDays}
            value={desde}
            onChange={(e) => setDesde(e.target.value)}
            className="min-w-40 flex-1"
          />
          <Input
            label="Hasta"
            type="date"
            icon={CalendarDays}
            value={hasta}
            onChange={(e) => setHasta(e.target.value)}
            className="min-w-40 flex-1"
          />
          <Button type="submit" variant="solid" disabled={cargando}>
            Generar reporte
          </Button>
        </div>
        <div className="mt-3 flex flex-wrap gap-x-6 gap-y-2 text-sm">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={graficos}
              onChange={(e) => setGraficos(e.target.checked)}
              className="h-4 w-4 accent-primary"
            />
            Incluir gráficos
          </label>
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={analisis}
              onChange={(e) => setAnalisis(e.target.checked)}
              className="h-4 w-4 accent-primary"
            />
            Incluir análisis
          </label>
        </div>
        <p className="mt-2 text-[11px] text-muted">
          Deja las fechas vacías para incluir todos tus movimientos. Los archivos se exportan en soles (PEN) con las mismas opciones.
        </p>
      </form>

      {error && (
        <p role="alert" className="mb-4 rounded-xl border border-expense-soft bg-expense-soft/60 px-4 py-2.5 text-sm text-expense">
          {error}
        </p>
      )}

      {cargando && !reporte && <p className="py-10 text-center text-sm text-muted">Generando reporte…</p>}

      {reporte && (
        <div className={cargando ? 'opacity-60' : ''}>
          <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
            <p className="text-sm font-semibold">{describirPeriodo(reporte)}</p>
            <p className="text-[11px] text-muted">
              {reporte.cantidadMovimientos} movimiento(s) · Montos en {divisa.nombre} ({divisa.codigo})
            </p>
          </div>

          {!hayMovimientos ? (
            <p className="rounded-2xl bg-app py-10 text-center text-sm text-muted">
              No hay movimientos en el periodo seleccionado.
            </p>
          ) : (
            <>
              <div className="mb-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                <Card>
                  <CardTitle className="text-income">Ingresos</CardTitle>
                  <p className="text-xl font-bold text-income">{formatear(reporte.totalIngresos)}</p>
                </Card>
                <Card>
                  <CardTitle className="text-expense">Gastos</CardTitle>
                  <p className="text-xl font-bold text-expense">{formatear(reporte.totalGastos)}</p>
                </Card>
                <Card>
                  <CardTitle>Balance</CardTitle>
                  <p className={`text-xl font-bold ${reporte.balance < 0 ? 'text-expense' : 'text-ink'}`}>
                    {formatear(reporte.balance)}
                  </p>
                </Card>
                <Card>
                  <CardTitle>Tasa de ahorro</CardTitle>
                  <p className="text-xl font-bold">
                    {reporte.tasaAhorro === null ? '—' : `${reporte.tasaAhorro}%`}
                  </p>
                </Card>
              </div>

              {opciones.graficos && (
                <div className="mb-5 grid gap-5 lg:grid-cols-5">
                  <Card className="lg:col-span-3">
                    <CardTitle>Ingresos vs gastos por mes</CardTitle>
                    <div className="h-64">
                      <Bar data={datosBarras} options={opcionesBarras} />
                    </div>
                  </Card>
                  <Card className="lg:col-span-2">
                    <CardTitle>Gastos por categoría</CardTitle>
                    {reporte.gastosPorCategoria.length === 0 ? (
                      <p className="flex h-64 items-center justify-center text-sm text-muted">
                        No hay gastos en el periodo.
                      </p>
                    ) : (
                      <div className="h-64">
                        <Doughnut data={datosCategorias} options={opcionesCategorias} />
                      </div>
                    )}
                  </Card>
                </div>
              )}

              {opciones.analisis && reporte.observaciones.length > 0 && (
                <Card className="mb-5">
                  <CardTitle>Análisis financiero</CardTitle>
                  <ul className="divide-y divide-line/70">
                    {reporte.observaciones.map((observacion) => (
                      <li key={observacion.titulo} className="flex flex-wrap items-center gap-3 py-3 first:pt-0 last:pb-0">
                        <Badge tone={TONOS[observacion.nivel]}>{ETIQUETAS_NIVEL[observacion.nivel]}</Badge>
                        <div className="min-w-40 flex-1">
                          <p className="text-sm font-semibold">{observacion.titulo}</p>
                          <p className="text-xs text-muted">{observacion.mensaje}</p>
                        </div>
                        {observacion.monto !== null && (
                          <p className="text-sm font-semibold tabular-nums">{formatear(observacion.monto)}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                </Card>
              )}

              <Card className="mb-1">
                <CardTitle>Detalle de movimientos</CardTitle>
                <div className="overflow-x-auto">
                  <table className="w-full min-w-[520px] text-sm">
                    <thead>
                      <tr className="label-caps border-b border-line text-left">
                        <th className="px-2 pb-2 font-semibold">Fecha</th>
                        <th className="px-2 pb-2 font-semibold">Descripción</th>
                        <th className="px-2 pb-2 font-semibold">Tipo</th>
                        <th className="px-2 pb-2 text-right font-semibold">Monto</th>
                      </tr>
                    </thead>
                    <tbody>
                      {reporte.movimientos.map((movimiento) => {
                        const ingreso = movimiento.tipo === 'INGRESO'
                        return (
                          <tr key={movimiento.id} className="border-b border-line/70 last:border-0">
                            <td className="px-2 py-2.5 text-muted">{formatearFecha(movimiento.fecha)}</td>
                            <td className="px-2 py-2.5 font-medium">{movimiento.descripcion || '—'}</td>
                            <td className="px-2 py-2.5">
                              <Badge tone={ingreso ? 'income' : 'expense'}>{ingreso ? 'Ingreso' : 'Gasto'}</Badge>
                            </td>
                            <td className={`px-2 py-2.5 text-right font-semibold tabular-nums ${ingreso ? 'text-income' : 'text-ink'}`}>
                              {ingreso ? '+' : '-'} {formatear(movimiento.montoEnSoles)}
                            </td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            </>
          )}
        </div>
      )}
    </PageContainer>
  )
}

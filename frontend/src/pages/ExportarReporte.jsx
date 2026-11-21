import { useState } from 'react'
import { Button, Card, CardTitle, PageContainer, Placeholder } from '../components/ui'
import { PATHS } from '../routes/paths.js'
import { descargarReporteFinanciero } from '../services/api.js'
import ExportarConDivisa from '../components/ExportarConDivisa.jsx'

export default function ExportarReporte() {
    const [fecha, setFecha] = useState('')
    const [error, setError] = useState('')
    const [cargando, setCargando] = useState(false)

    async function exportarReporte(event) {
        event.preventDefault()
        if (!fecha) return setError('Por favor, selecciona un mes para exportar el reporte.')
        const [anio, mes] = fecha.split('-')
        const desde = `${anio}-${mes}-01`
        const hasta = new Date(Number(anio), Number(mes), 0).toISOString().slice(0, 10)
        setError('')
        setCargando(true)
        try {
            await descargarReporteFinanciero({ desde, hasta, graficos: true, analisis: true }, 'pdf')
        } catch (e) {
            setError(e.message)
        } finally {
            setCargando(false)
        }
    }

    return (
        <PageContainer title="Exportar reporte" backTo={PATHS.reportes}>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
                <Card className="md:col-span-2">
                    <CardTitle>Vista previa del reporte</CardTitle>
                    <Placeholder />
                </Card>
                <Card>
                    <CardTitle>Exportar reporte</CardTitle>
                    <div>
                        <form onSubmit={exportarReporte}>
                            <input
                                className="rounded border border-line px-3 py-2"
                                type="month"
                                value={fecha}
                                onChange={(e) => setFecha(e.target.value)}
                            />
                            {error && (
                                <p className="mt-2 text-sm text-red-600" role="alert">
                                    {error}
                                </p>
                            )}
                            <Button type="submit" size="lg" block disabled={cargando} className="mt-10 hover:cursor-pointer hover:scale-105">
                                {cargando ? 'Generando PDF...' : 'Exportar reporte'}
                            </Button>
                        </form>
                    </div>
                </Card>
                <ExportarConDivisa />
            </div>
        </PageContainer>
    )
}

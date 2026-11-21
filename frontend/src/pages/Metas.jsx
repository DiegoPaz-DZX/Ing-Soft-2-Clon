import {Plus, ArrowDown, Trash2, Pencil, Check, X} from 'lucide-react'
import {Button, Card, CardTitle} from '../components/ui'
import {useState, useMemo, useEffect} from 'react'
import {useTransacciones} from '../context/TransaccionesContext.jsx'
import {useMoneda} from '../context/MonedaContext.jsx'
import {obtenerMovimientos} from '../services/api.js'
import BarraMeta from '../components/metas/BarraMeta.jsx'
import ConversorDivisa from '../domain/ConversorDivisa.js'
import ServicioMetas from '../services/ServicioMetas.js'
import RepositorioMetasApi from '../repositories/RepositorioMetasApi.js'

const TIPO_CAMBIO_RESPALDO = 3.75
const servicioMetas = new ServicioMetas(new RepositorioMetasApi())

export default function Metas() {
    const [mostrarForm, setMostrarForm] = useState(false)
    const [nombreMeta, setNombreMeta] = useState('')
    const [montoMeta, setMontoMeta] = useState('')
    const [error, setError] = useState('')
    const [metas, setMetas] = useState([])
    const [cargando, setCargando] = useState(true)
    const [eliminandoId, setEliminandoId] = useState(null)
    const [editandoId, setEditandoId] = useState(null)
    const [nombreEdicion, setNombreEdicion] = useState('')
    const [guardandoNombre, setGuardandoNombre] = useState(false)
    const [movimientosPersistidos, setMovimientosPersistidos] = useState([])
    const [movimientosCargados, setMovimientosCargados] = useState(false)
    const {transacciones} = useTransacciones()
    const {divisa, tipoCambio, formatear} = useMoneda()

    // Se recalcula cuando cambia la divisa del perfil
    const conversor = useMemo(() => new ConversorDivisa(divisa), [divisa])
    const solesPorDolar = tipoCambio?.solesPorDolar ?? TIPO_CAMBIO_RESPALDO

    useEffect(() => {
        servicioMetas.obtener().then(setMetas).catch((err) => setError(err.message)).finally(() => setCargando(false))
        obtenerMovimientos()
            .then(setMovimientosPersistidos)
            .catch(() => setMovimientosPersistidos([]))
            .finally(() => setMovimientosCargados(true))
    }, [])

    const movimientosParaProgreso = movimientosCargados ? movimientosPersistidos : transacciones
    const ahorrosSinMeta = movimientosParaProgreso.filter(
        (transaccion) =>
            String(transaccion.tipo).toLowerCase() === 'gasto' &&
            String(transaccion.categoria).toLowerCase() === 'ahorro' &&
            !transaccion.metaId &&
            !transaccion.meta_id,
    ).length

    const progreso = useMemo(
        () => metas.map((meta) => ({
            meta,
            progreso: servicioMetas.calcularProgreso(meta, movimientosParaProgreso, solesPorDolar),
        })),
        [metas, movimientosParaProgreso, solesPorDolar],
    )

    async function registrarMeta(e) {
        e.preventDefault()

        try {
            const nuevaMeta = await servicioMetas.crear({nombre: nombreMeta, objetivo: montoMeta}, conversor)
            setMetas((actuales) => [...actuales, nuevaMeta])
            setNombreMeta('')
            setMontoMeta('')
            setError('')
            setMostrarForm(false)
        } catch (err) {
            setError(err.message)
        }
    }

    async function eliminar(meta) {
        if (!window.confirm(`¿Eliminar la meta "${meta.nombre}"? Esta acción no se puede deshacer.`)) return

        try {
            setEliminandoId(meta.id)
            await servicioMetas.eliminar(meta)
            setMetas((actuales) => actuales.filter((actual) => actual.id !== meta.id))
            setError('')
        } catch (err) {
            setError(err.message)
        } finally {
            setEliminandoId(null)
        }
    }

    function iniciarEdicion(meta) {
        setEditandoId(meta.id)
        setNombreEdicion(meta.nombre)
        setError('')
    }

    function cancelarEdicion() {
        setEditandoId(null)
        setNombreEdicion('')
    }

    async function guardarNombre(meta) {
        try {
            setGuardandoNombre(true)
            const metaActualizada = await servicioMetas.renombrar(meta, nombreEdicion)
            setMetas((actuales) => actuales.map((actual) => (
                actual.id === metaActualizada.id ? metaActualizada : actual
            )))
            cancelarEdicion()
            setError('')
        } catch (err) {
            setError(err.message)
        } finally {
            setGuardandoNombre(false)
        }
    }

    return (
        <section className = "grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
            <Card className = "sm:col-span-2 xl:col-span-3">
                <CardTitle>
                    <span className = "flex items-center gap-4"><ArrowDown size = {16}/>Mis metas de ahorro</span>
                </CardTitle>
                <p className = "text-sm text-muted">
                    Crea objetivos con nombres diferentes y realiza abonos desde cada tarjeta.
                </p>
                {ahorrosSinMeta > 0 && (
                    <p className = "mt-3 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
                        Tienes {ahorrosSinMeta} ahorro(s) sin meta asignada. Edita esas transacciones
                        desde “Transacciones” para indicar a qué meta pertenecen.
                    </p>
                )}
            </Card>
            <Card className = "self-start sm:col-span-2 xl:col-span-1">
                <CardTitle>
                    <span className = "flex items-center gap-4"><ArrowDown size = {16}/>Nueva Meta</span>
                </CardTitle>
                <Button onClick = {() => setMostrarForm((visible) => !visible)} size = "lg" block
                        className = "hover:scale-105 duration-300 transition-all hover:cursor-pointer">
                    <Plus size = {12}/> Nueva Meta
                </Button>
                {mostrarForm && (
                    <Card className = "mt-4">
                        <form onSubmit = {registrarMeta} className = "grid gap-2">
                            <input
                                type = "text"
                                placeholder = "Nombre de la meta"
                                aria-label = "Nombre de la meta"
                                required
                                className = "border border-gray-300 rounded-md p-2 w-full mt-2"
                                value = {nombreMeta}
                                onChange = {(e) => setNombreMeta(e.target.value)}
                            />
                            <input
                                type = "number"
                                min = "0"
                                step = "0.01"
                                placeholder = {`${divisa.simbolo} `}
                                aria-label = "Monto objetivo"
                                required
                                className = "border border-gray-300 rounded-md p-2 w-full mt-2"
                                value = {montoMeta}
                                onChange = {(e) => setMontoMeta(e.target.value)}
                            />
                            {error && (
                                <p role = "alert" className = "text-sm text-red-600">
                                    {error}
                                </p>
                            )}
                            <Button type = "submit" size = "lg" block
                                    className = "hover:scale-105 mt-2 hover:cursor-pointer">
                                Registrar meta
                            </Button>
                        </form>
                    </Card>
                )}
            </Card>
            <Card className = "sm:col-span-2 xl:col-span-2">
                <CardTitle>
                    <span className = "flex items-center gap-4"><ArrowDown size = {16}/>Objetivos registrados</span>
                </CardTitle>
                {error && !mostrarForm && (
                    <p role = "alert" className = "mb-3 text-sm text-red-600">{error}</p>
                )}
                {cargando ? <p className = "text-sm text-muted">Cargando metas...</p> : progreso.length ? (
                    <div className = "grid gap-4 sm:grid-cols-2">
                        {progreso.map(({meta, progreso: avance}) => (
                            <Card
                                key = {meta.id}
                                className = "group border-line shadow-none transition-all duration-300 hover:-translate-y-1 hover:scale-[1.02] hover:shadow-lg"
                            >
                                <div className = "flex items-start justify-between gap-3">
                                    <div className = "min-w-0 flex-1">
                                        {editandoId === meta.id ? (
                                            <form
                                                className = "flex items-center gap-2"
                                                onSubmit = {(e) => {
                                                    e.preventDefault()
                                                    guardarNombre(meta)
                                                }}
                                            >
                                                <input
                                                    type = "text"
                                                    value = {nombreEdicion}
                                                    maxLength = "120"
                                                    aria-label = "Nuevo nombre de la meta"
                                                    autoFocus
                                                    className = "min-w-0 flex-1 rounded-lg border border-primary p-2 text-sm"
                                                    onChange = {(e) => setNombreEdicion(e.target.value)}
                                                />
                                                <Button
                                                    type = "submit"
                                                    variant = "ghost"
                                                    size = "sm"
                                                    aria-label = "Guardar nombre"
                                                    disabled = {guardandoNombre}
                                                    className = "text-income"
                                                >
                                                    <Check size = {16}/>
                                                </Button>
                                                <Button
                                                    type = "button"
                                                    variant = "ghost"
                                                    size = "sm"
                                                    aria-label = "Cancelar edición"
                                                    disabled = {guardandoNombre}
                                                    onClick = {cancelarEdicion}
                                                >
                                                    <X size = {16}/>
                                                </Button>
                                            </form>
                                        ) : (
                                            <BarraMeta nombre = {meta.nombre} progreso = {avance} formatear = {formatear}/>
                                        )}
                                    </div>
                                    {editandoId !== meta.id && (
                                        <div className = "flex shrink-0 gap-1 opacity-70 transition-opacity group-hover:opacity-100">
                                            <Button
                                                type = "button"
                                                variant = "ghost"
                                                size = "sm"
                                                aria-label = {`Renombrar meta ${meta.nombre}`}
                                                title = "Renombrar meta"
                                                onClick = {() => iniciarEdicion(meta)}
                                                className = "text-primary hover:text-primary-dark"
                                            >
                                                <Pencil size = {16}/>
                                            </Button>
                                            <Button
                                                type = "button"
                                                variant = "ghost"
                                                size = "sm"
                                                aria-label = {`Eliminar meta ${meta.nombre}`}
                                                title = "Eliminar meta"
                                                disabled = {eliminandoId === meta.id}
                                                onClick = {() => eliminar(meta)}
                                                className = "text-red-600 hover:text-red-800"
                                            >
                                                <Trash2 size = {16}/>
                                            </Button>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        ))}
                    </div>
                ) : (
                    <p className = "text-sm text-muted">
                        Aún no tienes metas. Usa “Nueva meta” para registrar tu primer objetivo.
                    </p>
                )}
            </Card>
        </section>
    )
}

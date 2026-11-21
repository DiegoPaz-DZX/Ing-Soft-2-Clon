from datetime import date

from .Recomendacion import Recomendacion
from .ReglaAhorro import ReglaAhorro
from .ReglaAumento import ReglaAumento
from .ReglaCategoriaPrincipal import ReglaCategoriaPrincipal  # NUEVO
from .ReglaConcentracion import ReglaConcentracion
from .ReglaDeficit import ReglaDeficit
from .ReglaGastoSobreIngresos import ReglaGastoSobreIngresos  # NUEVO
from .ReglaReduccion import ReglaReduccion  # NUEVO
from .ReglaSinIngresos import ReglaSinIngresos  # NUEVO
from .ResumenMensual import ResumenMensual

MINIMO_MOVIMIENTOS = 3
MINIMO_RECOMENDACIONES = 4  # NUEVO: cuántas tarjetas como mínimo
ORDEN_NIVEL = {"advertencia": 0, "informacion": 1, "positivo": 2}

# NUEVO: consejos generales para completar el mínimo
CONSEJOS_GENERALES = [
    Recomendacion(
        id="consejo-registro-diario",
        nivel="informacion",
        titulo="Registra tus gastos a diario",
        mensaje="Anotar cada gasto el mismo día evita olvidos y hace que tus recomendaciones sean más precisas.",
    ),
    Recomendacion(
        id="consejo-fondo-emergencia",
        nivel="informacion",
        titulo="Crea un fondo de emergencia",
        mensaje="Intenta reunir de 3 a 6 meses de tus gastos básicos para imprevistos.",
    ),
    Recomendacion(
        id="consejo-meta-ahorro",
        nivel="informacion",
        titulo="Define una meta de ahorro",
        mensaje="Ahorrar con un objetivo concreto (un viaje, un equipo) es más fácil que ahorrar 'lo que sobre'.",
    ),
    Recomendacion(
        id="consejo-revisar-suscripciones",
        nivel="informacion",
        titulo="Revisa tus pagos recurrentes",
        mensaje="Cancela suscripciones y servicios que ya no usas: son gastos pequeños que se acumulan.",
    ),
]


class ServicioRecomendaciones:
    def __init__(self, repositorio_movimientos, servicio_categorias):
        self._repositorio = repositorio_movimientos
        self._categorias = servicio_categorias
        self._reglas = [
            ReglaSinIngresos(),  # NUEVO
            ReglaDeficit(),
            ReglaConcentracion(),
            ReglaCategoriaPrincipal(),  # NUEVO
            ReglaAumento(),
            ReglaReduccion(),  # NUEVO
            ReglaAhorro(),
            ReglaGastoSobreIngresos(),  # NUEVO
        ]

    def obtener_recomendaciones(self, cuenta, hoy=None):
        hoy = hoy or date.today()
        nombres = {c.codigo: c.nombre for c in self._categorias.obtener_todas()}
        # NUEVO: las reglas comparan montos, así que solo se usan los movimientos en soles
        movimientos_en_soles = [
            m for m in self._repositorio.listar_todos(cuenta) if m.moneda == "PEN"
        ]
        resumen = ResumenMensual(movimientos_en_soles, hoy, nombres)

        # Lista vacía = "aún no hay suficientes datos" para el frontend
        if resumen.cantidad < MINIMO_MOVIMIENTOS:
            return []

        recomendaciones = []
        for regla in self._reglas:
            recomendaciones.extend(regla.evaluar(resumen))

        # NUEVO: completa con consejos generales hasta llegar al mínimo
        for consejo in CONSEJOS_GENERALES:
            if len(recomendaciones) >= MINIMO_RECOMENDACIONES:
                break
            recomendaciones.append(consejo)

        return sorted(recomendaciones, key=lambda r: ORDEN_NIVEL[r.nivel])
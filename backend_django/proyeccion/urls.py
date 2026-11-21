from django.urls import path
from config.FabricaServicios import FabricaServicios
from historial.RepositorioHistorialDjango import RepositorioHistorialDjango
from .DetectorGastoAtipico import DetectorGastoAtipico
from .ManejadorProyeccion import ManejadorProyeccion
from .ProyeccionPorRitmoDiario import ProyeccionPorRitmoDiario
from .ServicioProyeccion import ServicioProyeccion

servicio = ServicioProyeccion(
    RepositorioHistorialDjango(), ProyeccionPorRitmoDiario(), DetectorGastoAtipico()
)

urlpatterns = [
    path("proyeccion", ManejadorProyeccion.as_view(
        servicio=servicio, servicio_tokens=FabricaServicios.crear_servicio_tokens()
    )),
]
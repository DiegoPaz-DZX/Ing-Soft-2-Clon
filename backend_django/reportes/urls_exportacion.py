from django.urls import path
from config.FabricaServicios import FabricaServicios
from .ManejadorExportacionReporte import ManejadorExportacionReporte
from .ServicioExportacionReporte import ServicioExportacionReporte

servicio = ServicioExportacionReporte(
    FabricaServicios.crear_servicio_reportes(),
    FabricaServicios.crear_servicio_preferencias(),
)

urlpatterns = [
    path(
        "reportes/financiero/exportar",
        ManejadorExportacionReporte.as_view(
            servicio=servicio,
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]
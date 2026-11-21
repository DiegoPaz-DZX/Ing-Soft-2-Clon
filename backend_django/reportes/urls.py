from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorMonitorSalud import ManejadorMonitorSalud
from .ManejadorReporte import ManejadorReporte
from .MonitorSaludFacade import MonitorSaludFacade

urlpatterns = [
    path(
        "reportes/financiero",
        ManejadorReporte.as_view(
            servicio=FabricaServicios.crear_servicio_reportes(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
    path(
        "monitor/salud",
        ManejadorMonitorSalud.as_view(
            servicio=MonitorSaludFacade(FabricaServicios.crear_servicio_reportes()),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

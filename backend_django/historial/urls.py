from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorHistorial import ManejadorHistorial

urlpatterns = [
    path(
        "movimientos",
        ManejadorHistorial.as_view(
            servicio=FabricaServicios.crear_historial_movimientos(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

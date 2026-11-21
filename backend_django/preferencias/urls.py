from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorPreferenciaMoneda import ManejadorPreferenciaMoneda

urlpatterns = [
    path(
        "preferencias/moneda",
        ManejadorPreferenciaMoneda.as_view(
            servicio=FabricaServicios.crear_servicio_preferencias(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

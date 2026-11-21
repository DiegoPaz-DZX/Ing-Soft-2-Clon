from django.urls import path
from config.FabricaServicios import FabricaServicios
from .ManejadorAlertas import ManejadorAlertas
from .ManejadorLimites import ManejadorLimites

urlpatterns = [
    path(
        "alertas",
        ManejadorAlertas.as_view(
            servicio=FabricaServicios.crear_servicio_alertas(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
    path(
        "limites",
        ManejadorLimites.as_view(
            servicio=FabricaServicios.crear_servicio_alertas(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

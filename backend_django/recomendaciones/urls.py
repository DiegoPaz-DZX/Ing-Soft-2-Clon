from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorRecomendaciones import ManejadorRecomendaciones

urlpatterns = [
    path(
        "recomendaciones",
        ManejadorRecomendaciones.as_view(
            servicio=FabricaServicios.crear_servicio_recomendaciones(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]
from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorTips import ManejadorTips

urlpatterns = [
    path("tips", ManejadorTips.as_view(servicio=FabricaServicios.crear_servicio_tips())),
]

from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorMetas import ManejadorMetas

facade = FabricaServicios.crear_facade_metas()

urlpatterns = [
    path("metas", ManejadorMetas.as_view(facade=facade)),
    path("metas/<int:meta_id>", ManejadorMetas.as_view(facade=facade)),
    path("metas/<int:meta_id>/abonos", ManejadorMetas.as_view(facade=facade)),
]

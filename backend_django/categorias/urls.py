from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorCategorias import ManejadorCategorias

urlpatterns = [
    path(
        "categorias",
        ManejadorCategorias.as_view(servicio=FabricaServicios.crear_servicio_categorias()),
    ),
]

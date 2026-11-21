from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorBalance import ManejadorBalance
from .ManejadorEliminarMovimiento import ManejadorEliminarMovimiento  # NUEVO
from .ManejadorMovimientos import ManejadorMovimientos
from .ManejadorEdicionMovimientos import ManejadorEdicionMovimientos
from .ManejadorImportacionMovimientos import ManejadorImportacionMovimientos

urlpatterns = [
    path("balance", ManejadorBalance.as_view(servicio=FabricaServicios.crear_servicio_balance(), servicio_tokens = FabricaServicios.crear_servicio_tokens())),
    path(
        "movimientos/nuevo",
        ManejadorMovimientos.as_view(
            servicio=FabricaServicios.crear_servicio_movimientos(),
            servicio_tokens = FabricaServicios.crear_servicio_tokens()
        ),
    ),
    path(
        "movimientos/importar",
        ManejadorImportacionMovimientos.as_view(
            servicio=FabricaServicios.crear_servicio_importacion_movimientos(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
    path(
        "movimientos/<int:movimiento_id>/editar",
        ManejadorEdicionMovimientos.as_view(
            servicio=FabricaServicios.crear_servicio_movimientos(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
    # NUEVO
    path(
        "movimientos/<int:movimiento_id>/eliminar",
        ManejadorEliminarMovimiento.as_view(
            servicio=FabricaServicios.crear_servicio_movimientos(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

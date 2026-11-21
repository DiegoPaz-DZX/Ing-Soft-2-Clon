from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorRegistro import ManejadorRegistro
from .ManejadorCambioClave import ManejadorCambioClave
from .ManejadorAdministracionUsuarios import ManejadorAdministracionUsuarios

urlpatterns = [
    path(
        "registro",
        ManejadorRegistro.as_view(servicio=FabricaServicios.crear_servicio_registro()),
    ),
    path(
        "cambiar-clave",
        ManejadorCambioClave.as_view(servicio=FabricaServicios.crear_servicio_cambio_clave()),
    ),
    path(
        "admin/usuarios",
        ManejadorAdministracionUsuarios.as_view(
            servicio=FabricaServicios.crear_servicio_administracion_usuarios()
        ),
    ),
    path(
        "admin/usuarios/<int:cuenta_id>/rol",
        ManejadorAdministracionUsuarios.as_view(
            servicio=FabricaServicios.crear_servicio_administracion_usuarios()
        ),
    ),
]

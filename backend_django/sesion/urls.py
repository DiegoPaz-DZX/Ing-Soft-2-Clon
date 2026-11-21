from django.urls import path

from config.FabricaServicios import FabricaServicios

from .ManejadorLogin import ManejadorLogin
from .ManejadorLogout import ManejadorLogout

urlpatterns = [
    path(
        "login",
        ManejadorLogin.as_view(
            servicio=FabricaServicios.crear_proveedor_autenticacion(),
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
    path(
        "logout",
        ManejadorLogout.as_view(
            servicio_tokens=FabricaServicios.crear_servicio_tokens(),
        ),
    ),
]

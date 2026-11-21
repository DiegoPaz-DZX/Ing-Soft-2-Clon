from django.conf import settings  # NUEVO
from django.conf.urls.static import static  # NUEVO
from django.urls import include, path

urlpatterns = [
    path("api/", include("balance.urls")),
    path("api/", include("categorias.urls")),
    path("api/", include("tips.urls")),
    path("api/", include("usuarios.urls")),
    path("api/", include("alertas.urls")),
    path("api/", include("historial.urls")),
    path("api/", include("sesion.urls")),
    path("api/", include("recomendaciones.urls")), 
    path("api/", include("preferencias.urls")),
    path("api/", include("reportes.urls")),
    path("api/", include("reportes.urls_exportacion")),
    path("api/", include("proyeccion.urls")),
    path("api/", include("metas.urls")),
]

# NUEVO: sirve los archivos subidos (solo funciona en desarrollo, con DEBUG = True)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
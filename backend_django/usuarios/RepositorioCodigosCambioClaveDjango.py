from .CodigoCambioClave import CodigoCambioClave
from .RepositorioCodigosCambioClave import RepositorioCodigosCambioClave


class RepositorioCodigosCambioClaveDjango(RepositorioCodigosCambioClave):
    def invalidar_activos(self, cuenta):
        CodigoCambioClave.objects.filter(cuenta=cuenta, usado=False).update(usado=True)

    def crear(self, cuenta, codigo_hash, expira_en):
        return CodigoCambioClave.objects.create(
            cuenta=cuenta,
            codigo_hash=codigo_hash,
            expira_en=expira_en,
        )

    def obtener_pendiente(self, cuenta):
        return (
            CodigoCambioClave.objects.select_for_update()
            .filter(cuenta=cuenta, usado=False)
            .order_by("-creado_en")
            .first()
        )

    def guardar_intentos(self, solicitud):
        solicitud.save(update_fields=["intentos"])

    def marcar_usado(self, solicitud):
        solicitud.usado = True
        solicitud.save(update_fields=["usado"])

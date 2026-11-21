from .models import TokenRevocado
from .RepositorioTokensRevocados import RepositorioTokensRevocados


class RepositorioTokensRevocadosDjango(RepositorioTokensRevocados):
    def revocar(self, huella, expira_en):
        TokenRevocado.objects.update_or_create(
            huella=huella,
            defaults={"expira_en": expira_en},
        )

    def esta_revocado(self, huella, ahora):
        return TokenRevocado.objects.filter(
            huella=huella,
            expira_en__gt=ahora,
        ).exists()

    def eliminar_expirados(self, ahora):
        TokenRevocado.objects.filter(expira_en__lte=ahora).delete()

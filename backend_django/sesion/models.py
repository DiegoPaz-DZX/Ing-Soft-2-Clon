from django.db import models


class TokenRevocado(models.Model):
    huella = models.CharField(max_length=64, unique=True)
    expira_en = models.DateTimeField()
    revocado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["expira_en"])]

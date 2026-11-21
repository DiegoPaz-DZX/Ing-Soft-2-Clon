from django.db import models


class TipoMovimiento(models.TextChoices):
    INGRESO = "INGRESO", "Ingreso"
    GASTO = "GASTO", "Gasto"

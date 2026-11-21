from django.db import models


class TipoCambioDiario(models.Model):
    fecha = models.DateField(unique=True)
    soles_por_dolar = models.DecimalField(max_digits=10, decimal_places=4)
    fuente = models.CharField(max_length=60)

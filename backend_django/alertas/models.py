from django.db import models

class LimiteGasto(models.Model):
    usuario_id = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    limite_mensual = models.DecimalField(max_digits=12, decimal_places=2)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('usuario_id', 'categoria')

class Alerta(models.Model):
    TIPOS = [('advertencia', 'Advertencia'), ('critica', 'Crítica')]
    usuario_id = models.CharField(max_length=100)
    categoria = models.CharField(max_length=50)
    tipo_alerta = models.CharField(max_length=20, choices=TIPOS)
    porcentaje_usado = models.DecimalField(max_digits=5, decimal_places=2)
    monto_limite = models.DecimalField(max_digits=12, decimal_places=2)
    monto_gastado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)
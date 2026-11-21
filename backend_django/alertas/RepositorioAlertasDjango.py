from .RepositorioAlertas import RepositorioAlertas
from .models import Alerta as AlertaModel
from .Alerta import Alerta
from .TipoAlerta import TipoAlerta

class RepositorioAlertasDjango(RepositorioAlertas):
    def guardar_alerta(self, alerta):
        AlertaModel.objects.create(
            usuario_id=alerta.usuario_id, categoria=alerta.categoria,
            tipo_alerta=alerta.tipo_alerta.value, porcentaje_usado=alerta.porcentaje_usado,
            monto_limite=alerta.monto_limite, monto_gastado=alerta.monto_gastado
        )
    
    def obtener_alertas_usuario(self, usuario_id):
        alertas_model = AlertaModel.objects.filter(usuario_id=usuario_id, leida=False).order_by('-fecha_creacion')
        return [
            Alerta(alerta.usuario_id, alerta.categoria, TipoAlerta(alerta.tipo_alerta),
                   alerta.porcentaje_usado, alerta.monto_limite, alerta.monto_gastado)
            for alerta in alertas_model
        ]
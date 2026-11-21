from decimal import Decimal

class Alerta:
    def __init__(self, usuario_id, categoria, tipo_alerta, porcentaje_usado, monto_limite, monto_gastado):
        self.usuario_id = usuario_id
        self.categoria = categoria
        self.tipo_alerta = tipo_alerta
        self.porcentaje_usado = Decimal(str(porcentaje_usado))
        self.monto_limite = Decimal(str(monto_limite))
        self.monto_gastado = Decimal(str(monto_gastado))
    
    def a_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'categoria': self.categoria,
            'tipo_alerta': self.tipo_alerta.value,
            'porcentaje_usado': float(self.porcentaje_usado),
            'monto_limite': float(self.monto_limite),
            'monto_gastado': float(self.monto_gastado),
            'descripcion': self.tipo_alerta.describe(),
        }
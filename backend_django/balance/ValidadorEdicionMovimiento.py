class ValidadorEdicionMovimiento:
    """Decorator que valida cambios en edición de movimiento"""
    def __init__(self, movimiento):
        self._movimiento = movimiento
    
    def validar_cambios(self, tipo=None, monto=None, fecha=None, descripcion=None, categoria=None):
        if monto is not None and float(monto) <= 0:
            raise ValueError("El monto debe ser mayor que cero")
        if tipo is not None and tipo not in ["INGRESO", "GASTO"]:
            raise ValueError("Tipo inválido")
        if fecha is not None:
            try:
                from datetime import date
                date.fromisoformat(str(fecha))
            except ValueError:
                raise ValueError("Fecha inválida (AAAA-MM-DD)")
        return True
    
    def obtener_movimiento(self):
        return self._movimiento
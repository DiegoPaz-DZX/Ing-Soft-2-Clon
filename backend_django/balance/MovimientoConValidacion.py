from decimal import Decimal
from .MovimientoDecorador import MovimientoDecorador
from .DatosMovimientoInvalidosException import DatosMovimientoInvalidosException
from .MontoInvalidoException import MontoInvalidoException
from datetime import date

class MovimientoConValidacion(MovimientoDecorador):
    """Decorator concreto que envuelve un Movimiento y valida su contenido antes de guardarlo"""
    
    def validar(self):
        """Ejecuta todas las validaciones sobre el movimiento envuelto"""
        movimiento = self._movimiento
        
        # Validar monto
        if not movimiento.monto or Decimal(str(movimiento.monto)) <= 0:
            raise MontoInvalidoException("El monto debe ser mayor que cero")
        
        # Validar tipo
        if not movimiento.tipo or movimiento.tipo not in ["INGRESO", "GASTO"]:
            raise DatosMovimientoInvalidosException("El tipo debe ser INGRESO o GASTO")
        
        # Validar fecha
        if not movimiento.fecha:
            raise DatosMovimientoInvalidosException("La fecha es obligatoria")
        try:
            date.fromisoformat(str(movimiento.fecha))
        except (ValueError, TypeError):
            raise DatosMovimientoInvalidosException("La fecha debe estar en formato AAAA-MM-DD")
        
        # Validar moneda
        if movimiento.moneda not in ["PEN", "USD"]:
            raise DatosMovimientoInvalidosException("La moneda debe ser PEN o USD")
        
        # Validar categoría para gastos
        if movimiento.tipo == "GASTO" and not movimiento.categoria:
            raise DatosMovimientoInvalidosException("Los gastos deben tener una categoría")
        
        return True
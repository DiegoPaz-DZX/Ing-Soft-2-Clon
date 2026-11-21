from decimal import Decimal

# decide si un gasto es unico y muy alto
# se compara contra el promedio de los demas gastos del historial
class DetectorGastoAtipico:
    FACTOR = Decimal("3")
    MINIMO_OTROS_GASTOS = 2

    def es_atipico(self, gasto, historial_gastos):
        suma = Decimal("0")
        cantidad = 0

        for otro in historial_gastos:
            if otro is not gasto:
                suma += otro.monto
                cantidad += 1

        # con muy pocos gastos no hay forma de comparar
        if cantidad < self.MINIMO_OTROS_GASTOS:
            return False

        promedio = suma / cantidad
        return gasto.monto > promedio * self.FACTOR
class ConvertidorReporte:
    #Convierte todo el reporte usando ConversorMoneda

    def __init__(self, conversor):
        self._conversor = conversor

    def convertir(self, reporte):
        convertir = self._conversor.convertir

        ingresos = convertir(reporte.total_ingresos)
        gastos = convertir(reporte.total_gastos)

        categorias = []
        for categoria in reporte.gastos_por_categoria:
            categorias.append((categoria.nombre, convertir(categoria.monto), categoria.porcentaje))

        meses = []
        for mes in reporte.evolucion_mensual:
            meses.append((mes.etiqueta, convertir(mes.ingresos), convertir(mes.gastos)))

        movimientos = []
        for movimiento in reporte.movimientos:
            movimientos.append(
                (movimiento.fecha, str(movimiento.tipo), movimiento.descripcion, convertir(movimiento.monto_en_soles))
            )

        return {
            "divisa": self._conversor.codigo,
            "nombre_divisa": self._conversor.nombre,
            "simbolo": self._conversor.simbolo,
            "tipo_cambio": self._conversor.soles_por_unidad(),
            "desde": reporte.desde,
            "hasta": reporte.hasta,
            "ingresos": ingresos,
            "gastos": gastos,
            "balance": ingresos - gastos,
            "cantidad": reporte.cantidad_movimientos,
            "categorias": categorias,
            "meses": meses,
            "movimientos": movimientos,
        }
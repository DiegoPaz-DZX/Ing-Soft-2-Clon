class ConversorReporte:
    @staticmethod
    def a_dict(reporte):
        return {
            "desde": reporte.desde.isoformat() if reporte.desde else None,
            "hasta": reporte.hasta.isoformat() if reporte.hasta else None,
            "cantidadMovimientos": reporte.cantidad_movimientos,
            "totalIngresos": float(reporte.total_ingresos),
            "totalGastos": float(reporte.total_gastos),
            "balance": float(reporte.balance),
            "tasaAhorro": float(reporte.tasa_ahorro) if reporte.tasa_ahorro is not None else None,
            "solesPorDolar": float(reporte.soles_por_dolar) if reporte.soles_por_dolar else None,
            "gastosPorCategoria": [
                {
                    "codigo": categoria.codigo,
                    "nombre": categoria.nombre,
                    "monto": float(categoria.monto),
                    "porcentaje": float(categoria.porcentaje),
                }
                for categoria in reporte.gastos_por_categoria
            ],
            "evolucionMensual": [
                {
                    "periodo": mes.periodo,
                    "etiqueta": mes.etiqueta,
                    "ingresos": float(mes.ingresos),
                    "gastos": float(mes.gastos),
                }
                for mes in reporte.evolucion_mensual
            ],
            "observaciones": [
                {
                    "nivel": observacion.nivel,
                    "titulo": observacion.titulo,
                    "mensaje": observacion.mensaje,
                    "monto": float(observacion.monto) if observacion.monto is not None else None,
                }
                for observacion in reporte.observaciones
            ],
            "movimientos": [
                {
                    "id": movimiento.id,
                    "fecha": movimiento.fecha.isoformat(),
                    "tipo": movimiento.tipo,
                    "descripcion": movimiento.descripcion,
                    "categoria": movimiento.categoria,
                    "moneda": movimiento.moneda,
                    "monto": float(movimiento.monto),
                    "montoEnSoles": float(movimiento.monto_en_soles),
                }
                for movimiento in reporte.movimientos
            ],
        }

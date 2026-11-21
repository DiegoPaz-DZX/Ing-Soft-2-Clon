import csv
import io

from .ExportadorReporte import ExportadorReporte

MARCA_UTF8 = "﻿"


class ExportadorCsv(ExportadorReporte):
    extension = "csv"
    tipo_contenido = "text/csv; charset=utf-8"

    def exportar(self, reporte):
        salida = io.StringIO()
        hoja = csv.writer(salida, lineterminator="\n")

        hoja.writerow(["Reporte financiero Kyzen"])
        hoja.writerow(["Desde", reporte.desde or "Inicio"])
        hoja.writerow(["Hasta", reporte.hasta or "Hoy"])
        if reporte.soles_por_dolar:
            hoja.writerow(["Tipo de cambio (soles por dólar)", reporte.soles_por_dolar])
        hoja.writerow([])

        hoja.writerow(["Resumen"])
        hoja.writerow(["Ingresos (PEN)", reporte.total_ingresos])
        hoja.writerow(["Gastos (PEN)", reporte.total_gastos])
        hoja.writerow(["Balance (PEN)", reporte.balance])
        hoja.writerow(["Tasa de ahorro (%)", "" if reporte.tasa_ahorro is None else reporte.tasa_ahorro])
        hoja.writerow(["Movimientos", reporte.cantidad_movimientos])

        if reporte.gastos_por_categoria:
            hoja.writerow([])
            hoja.writerow(["Gastos por categoría"])
            hoja.writerow(["Categoría", "Monto (PEN)", "Porcentaje (%)"])
            for categoria in reporte.gastos_por_categoria:
                hoja.writerow([categoria.nombre, categoria.monto, categoria.porcentaje])

        if reporte.evolucion_mensual:
            hoja.writerow([])
            hoja.writerow(["Evolución mensual"])
            hoja.writerow(["Mes", "Ingresos (PEN)", "Gastos (PEN)"])
            for mes in reporte.evolucion_mensual:
                hoja.writerow([mes.etiqueta, mes.ingresos, mes.gastos])

        if reporte.observaciones:
            hoja.writerow([])
            hoja.writerow(["Análisis"])
            hoja.writerow(["Título", "Detalle", "Monto (PEN)"])
            for observacion in reporte.observaciones:
                monto = "" if observacion.monto is None else observacion.monto
                hoja.writerow([observacion.titulo, observacion.mensaje, monto])

        hoja.writerow([])
        hoja.writerow(["Movimientos"])
        hoja.writerow(["Fecha", "Tipo", "Descripción", "Categoría", "Moneda", "Monto", "Monto (PEN)"])
        for movimiento in reporte.movimientos:
            hoja.writerow(
                [
                    movimiento.fecha.isoformat(),
                    movimiento.tipo,
                    movimiento.descripcion,
                    movimiento.categoria,
                    movimiento.moneda,
                    movimiento.monto,
                    movimiento.monto_en_soles,
                ]
            )

        return MARCA_UTF8 + salida.getvalue()

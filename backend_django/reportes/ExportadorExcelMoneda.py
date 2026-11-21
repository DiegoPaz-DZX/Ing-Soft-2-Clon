import io
from openpyxl import Workbook
from .ExportadorReporte import ExportadorReporte

class ExportadorExcelMoneda(ExportadorReporte):
    extension = "xlsx"
    tipo_contenido = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    def exportar(self, reporte):
        divisa = reporte["divisa"]
        libro = Workbook()

        hoja = libro.active
        hoja.title = "Resumen"
        hoja.append(["Reporte financiero Kyzen"])
        hoja.append(["Desde", str(reporte["desde"])])
        hoja.append(["Hasta", str(reporte["hasta"])])
        hoja.append(["Moneda", reporte["nombre_divisa"] + " (" + divisa + ")"])
        hoja.append(["Tipo de cambio (soles por 1 " + divisa + ")", float(reporte["tipo_cambio"])])
        hoja.append([])
        hoja.append(["Ingresos (" + divisa + ")", float(reporte["ingresos"])])
        hoja.append(["Gastos (" + divisa + ")", float(reporte["gastos"])])
        hoja.append(["Balance (" + divisa + ")", float(reporte["balance"])])
        hoja.append(["Movimientos", reporte["cantidad"]])

        hoja = libro.create_sheet("Gastos por categoría")
        hoja.append(["Categoría", "Monto (" + divisa + ")", "Porcentaje (%)"])
        for nombre, monto, porcentaje in reporte["categorias"]:
            hoja.append([nombre, float(monto), float(porcentaje)])

        hoja = libro.create_sheet("Evolución mensual")
        hoja.append(["Mes", "Ingresos (" + divisa + ")", "Gastos (" + divisa + ")"])
        for etiqueta, ingresos, gastos in reporte["meses"]:
            hoja.append([etiqueta, float(ingresos), float(gastos)])

        hoja = libro.create_sheet("Movimientos")
        hoja.append(["Fecha", "Tipo", "Descripción", "Monto (" + divisa + ")"])
        for fecha, tipo, descripcion, monto in reporte["movimientos"]:
            hoja.append([fecha.isoformat(), tipo, descripcion, float(monto)])

        salida = io.BytesIO()
        libro.save(salida)
        return salida.getvalue()
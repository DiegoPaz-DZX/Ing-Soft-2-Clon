from .ExportadorReporte import ExportadorReporte

LINEAS_POR_PAGINA = 46


def dinero(reporte, monto):
    return reporte["simbolo"] + " " + format(monto, ",.2f")


class ExportadorPdfMoneda(ExportadorReporte):
    extension = "pdf"
    tipo_contenido = "application/pdf"

    def exportar(self, reporte):
        lineas = self._armar_lineas(reporte)

        paginas = []
        for inicio in range(0, len(lineas), LINEAS_POR_PAGINA):
            paginas.append(lineas[inicio:inicio + LINEAS_POR_PAGINA])
        return self._armar_pdf(paginas)

    def _armar_lineas(self, reporte):
        divisa = reporte["divisa"]
        lineas = [
            "Reporte financiero Kyzen",
            "Desde: " + str(reporte["desde"]) + "   Hasta: " + str(reporte["hasta"]),
            "Moneda: " + reporte["nombre_divisa"] + " (" + divisa + ")",
            "Tipo de cambio: 1 " + divisa + " = " + str(reporte["tipo_cambio"]) + " PEN",
            "",
            "RESUMEN",
            "Ingresos: " + dinero(reporte, reporte["ingresos"]),
            "Gastos: " + dinero(reporte, reporte["gastos"]),
            "Balance: " + dinero(reporte, reporte["balance"]),
            "Movimientos: " + str(reporte["cantidad"]),
            "",
            "GASTOS POR CATEGORIA",
        ]
        for nombre, monto, porcentaje in reporte["categorias"]:
            lineas.append("- " + nombre + ": " + dinero(reporte, monto) + " (" + str(porcentaje) + "%)")

        lineas.append("")
        lineas.append("EVOLUCION MENSUAL")
        for etiqueta, ingresos, gastos in reporte["meses"]:
            lineas.append(
                "- " + etiqueta + ": ingresos " + dinero(reporte, ingresos) + " | gastos " + dinero(reporte, gastos)
            )

        lineas.append("")
        lineas.append("MOVIMIENTOS (montos en " + divisa + ")")
        for fecha, tipo, descripcion, monto in reporte["movimientos"]:
            lineas.append(fecha.isoformat() + " | " + tipo + " | " + descripcion[:40] + " | " + dinero(reporte, monto))
        return lineas

    def _armar_pdf(self, paginas):
        ids_paginas = []
        for numero in range(len(paginas)):
            ids_paginas.append(4 + 2 * numero)

        referencias = " ".join(str(i) + " 0 R" for i in ids_paginas)
        objetos = {
            1: b"<< /Type /Catalog /Pages 2 0 R >>",
            2: ("<< /Type /Pages /Kids [" + referencias + "] /Count " + str(len(paginas)) + " >>").encode(),
            3: b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>",
        }
        for id_pagina, lineas in zip(ids_paginas, paginas):
            contenido = self._contenido(lineas)
            objetos[id_pagina] = (
                "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                "/Resources << /Font << /F1 3 0 R >> >> /Contents " + str(id_pagina + 1) + " 0 R >>"
            ).encode()
            objetos[id_pagina + 1] = (
                ("<< /Length " + str(len(contenido)) + " >>\nstream\n").encode() + contenido + b"\nendstream"
            )

        pdf = bytearray(b"%PDF-1.4\n")
        posiciones = {}
        for numero in sorted(objetos):
            posiciones[numero] = len(pdf)
            pdf += (str(numero) + " 0 obj\n").encode() + objetos[numero] + b"\nendobj\n"

        inicio_xref = len(pdf)
        total = len(objetos) + 1
        pdf += ("xref\n0 " + str(total) + "\n").encode() + b"0000000000 65535 f \n"
        for numero in sorted(objetos):
            pdf += (format(posiciones[numero], "010d") + " 00000 n \n").encode()
        pdf += ("trailer\n<< /Size " + str(total) + " /Root 1 0 R >>\nstartxref\n" + str(inicio_xref) + "\n%%EOF").encode()
        return bytes(pdf)

    def _contenido(self, lineas):
        partes = [b"BT /F1 10 Tf 50 750 Td 15 TL"]
        for linea in lineas:
            partes.append(b"(" + self._texto(linea) + b") Tj T*")
        partes.append(b"ET")
        return b"\n".join(partes)

    def _texto(self, texto):
        datos = texto.encode("cp1252", "replace")
        return datos.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")
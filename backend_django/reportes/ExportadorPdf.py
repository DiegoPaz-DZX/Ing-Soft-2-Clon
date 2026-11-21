from .ExportadorReporte import ExportadorReporte


class ExportadorPdf(ExportadorReporte):
    extension = "pdf"
    tipo_contenido = "application/pdf"

    def exportar(self, reporte):
        lineas = [
            "Reporte financiero Kyzen",
            f"Desde: {reporte.desde or 'Inicio'}",
            f"Hasta: {reporte.hasta or 'Hoy'}",
            f"Ingresos (PEN): {reporte.total_ingresos}",
            f"Gastos (PEN): {reporte.total_gastos}",
            f"Balance (PEN): {reporte.balance}",
            f"Movimientos: {reporte.cantidad_movimientos}",
        ]
        contenido = "BT /F1 12 Tf 50 780 Td "
        contenido += " ".join(f"({self._texto(linea)}) Tj 0 -22 Td" for linea in lineas)
        contenido += " ET"

        objetos = [
            "<< /Type /Catalog /Pages 2 0 R >>",
            "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
            "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            f"<< /Length {len(contenido.encode('latin-1'))} >>\nstream\n{contenido}\nendstream",
        ]

        pdf = "%PDF-1.4\n"
        posiciones = [0]
        for numero, objeto in enumerate(objetos, 1):
            posiciones.append(len(pdf.encode("latin-1")))
            pdf += f"{numero} 0 obj\n{objeto}\nendobj\n"

        inicio_xref = len(pdf.encode("latin-1"))
        pdf += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n"
        pdf += "".join(f"{posicion:010d} 00000 n \n" for posicion in posiciones[1:])
        pdf += f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF"
        return pdf.encode("latin-1")

    def _texto(self, texto):
        return str(texto).encode("latin-1", "replace").decode("latin-1").replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

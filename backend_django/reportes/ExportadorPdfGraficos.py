from django.utils import timezone

from .ColoresPdf import ColoresPdf
from .DocumentoPdf import DocumentoPdf
from .ExportadorReporte import ExportadorReporte
from .GraficoBarrasPdf import GraficoBarrasPdf
from .GraficoCircularPdf import GraficoCircularPdf

ANCHO = 595.28
ALTO = 841.89
MARGEN = 50
LIMITE_INFERIOR = 60
ALTO_FILA = 16
NIVELES = {
    "advertencia": ("Atención", ColoresPdf.ROJO_SUAVE, ColoresPdf.ROJO),
    "positivo": ("Bien", ColoresPdf.VERDE_SUAVE, ColoresPdf.VERDE),
    "informacion": ("Dato", ColoresPdf.MORADO_SUAVE, ColoresPdf.MORADO),
}
COLUMNAS = [("Fecha", MARGEN), ("Descripción", 112), ("Tipo", 318), ("Moneda", 370)]


def soles(monto):
    return "S/ {:,.2f}".format(monto)


def fecha_corta(fecha):
    return fecha.strftime("%d/%m/%Y")


class ExportadorPdfGraficos(ExportadorReporte):
    extension = "pdf"
    tipo_contenido = "application/pdf"

    def exportar(self, reporte):
        self._documento = DocumentoPdf(ANCHO, ALTO)
        self._nueva_pagina()
        self._dibujar_encabezado(reporte)
        self._dibujar_resumen(reporte)
        if reporte.evolucion_mensual:
            self._dibujar_evolucion(reporte)
        if reporte.gastos_por_categoria:
            self._dibujar_categorias(reporte)
        if reporte.observaciones:
            self._dibujar_analisis(reporte)
        self._dibujar_movimientos(reporte)
        self._numerar_paginas()
        return self._documento.generar()

    def _nueva_pagina(self):
        self._pagina = self._documento.nueva_pagina()
        self._y = ALTO - MARGEN

    def _reservar(self, alto):
        if self._y - alto < LIMITE_INFERIOR:
            self._nueva_pagina()

    def _titulo_seccion(self, texto, alto_contenido):
        self._reservar(34 + alto_contenido)
        self._pagina.texto(MARGEN, self._y - 14, texto, 13, negrita=True)
        self._pagina.linea(MARGEN, self._y - 21, ANCHO - MARGEN, self._y - 21, ColoresPdf.MORADO, 1)
        self._y -= 34

    def _dibujar_encabezado(self, reporte):
        pagina = self._pagina
        pagina.rectangulo(0, ALTO - 78, ANCHO, 78, ColoresPdf.MORADO)
        pagina.texto(MARGEN, ALTO - 42, "Reporte financiero Kyzen", 21, negrita=True, color=ColoresPdf.BLANCO)
        if reporte.desde and reporte.hasta:
            periodo = f"Del {fecha_corta(reporte.desde)} al {fecha_corta(reporte.hasta)}"
        else:
            periodo = "Todos los movimientos registrados"
        pagina.texto(MARGEN, ALTO - 62, periodo, 11, color=ColoresPdf.BLANCO)

        detalle = f"Generado el {fecha_corta(timezone.localdate())}  ·  Montos en soles (PEN)"
        if reporte.soles_por_dolar:
            detalle += f"  ·  Tipo de cambio: 1 USD = S/ {reporte.soles_por_dolar}"
        pagina.texto(MARGEN, ALTO - 98, detalle, 9, color=ColoresPdf.GRIS)
        self._y = ALTO - 114

    def _dibujar_resumen(self, reporte):
        tasa = "—" if reporte.tasa_ahorro is None else f"{reporte.tasa_ahorro}%"
        color_balance = ColoresPdf.ROJO if reporte.balance < 0 else ColoresPdf.TINTA
        tarjetas = [
            ("INGRESOS", soles(reporte.total_ingresos), ColoresPdf.VERDE),
            ("GASTOS", soles(reporte.total_gastos), ColoresPdf.ROJO),
            ("BALANCE", soles(reporte.balance), color_balance),
            ("TASA DE AHORRO", tasa, ColoresPdf.TINTA),
        ]
        separacion = 10
        ancho = (ANCHO - 2 * MARGEN - 3 * separacion) / 4
        alto = 52
        for indice, (etiqueta, valor, color) in enumerate(tarjetas):
            x = MARGEN + indice * (ancho + separacion)
            self._pagina.rectangulo(x, self._y - alto, ancho, alto, ColoresPdf.FONDO)
            self._pagina.borde(x, self._y - alto, ancho, alto)
            self._pagina.texto(x + 10, self._y - 18, etiqueta, 7.5, negrita=True, color=ColoresPdf.GRIS)
            self._pagina.texto(x + 10, self._y - 39, valor, 12.5, negrita=True, color=color)
        self._pagina.texto(
            MARGEN, self._y - alto - 16, f"{reporte.cantidad_movimientos} movimiento(s) en el periodo.", 9,
            color=ColoresPdf.GRIS,
        )
        self._y -= alto + 30

    def _dibujar_evolucion(self, reporte):
        alto = 180
        self._titulo_seccion("Ingresos vs gastos por mes", alto)
        GraficoBarrasPdf().dibujar(
            self._pagina, MARGEN, self._y - alto, ANCHO - 2 * MARGEN, alto, reporte.evolucion_mensual
        )
        self._y -= alto + 18

    def _dibujar_categorias(self, reporte):
        grafico = GraficoCircularPdf()
        alto = max(150, grafico.alto_leyenda(reporte.gastos_por_categoria) + 20)
        self._titulo_seccion("Gastos por categoría", alto)
        radio = 62
        grafico.dibujar(
            self._pagina, MARGEN + radio + 8, self._y - radio - 10, radio, reporte.gastos_por_categoria,
            MARGEN + 2 * radio + 50, self._y - 18, ANCHO - MARGEN,
        )
        self._y -= alto + 10

    def _dibujar_analisis(self, reporte):
        self._titulo_seccion("Análisis financiero", 40)
        for observacion in reporte.observaciones:
            self._reservar(40)
            etiqueta, fondo, color = NIVELES.get(observacion.nivel, NIVELES["informacion"])
            self._pagina.rectangulo(MARGEN, self._y - 16, 56, 15, fondo)
            self._pagina.texto_centrado(MARGEN + 28, self._y - 12, etiqueta, 8, negrita=True, color=color)
            self._pagina.texto(MARGEN + 66, self._y - 12, observacion.titulo, 10, negrita=True)
            self._pagina.texto(MARGEN + 66, self._y - 26, observacion.mensaje, 9, color=ColoresPdf.GRIS)
            if observacion.monto is not None:
                self._pagina.texto_derecha(ANCHO - MARGEN, self._y - 12, soles(observacion.monto), 10, negrita=True)
            self._y -= 38

    def _dibujar_movimientos(self, reporte):
        self._titulo_seccion(f"Detalle de movimientos ({len(reporte.movimientos)})", ALTO_FILA * 2)
        if not reporte.movimientos:
            self._pagina.texto(MARGEN, self._y - 12, "No hay movimientos en el periodo seleccionado.", 10,
                               color=ColoresPdf.GRIS)
            self._y -= 24
            return
        self._dibujar_cabecera_tabla()
        for numero, movimiento in enumerate(reporte.movimientos):
            if self._y - ALTO_FILA < LIMITE_INFERIOR:
                self._nueva_pagina()
                self._dibujar_cabecera_tabla()
            if numero % 2:
                self._pagina.rectangulo(MARGEN, self._y - ALTO_FILA, ANCHO - 2 * MARGEN, ALTO_FILA, ColoresPdf.FONDO)
            ingreso = movimiento.tipo == "INGRESO"
            simbolo = "$" if movimiento.moneda == "USD" else "S/"
            texto_y = self._y - 11.5
            self._pagina.texto(MARGEN + 4, texto_y, fecha_corta(movimiento.fecha), 8.5)
            self._pagina.texto(112, texto_y, self._recortar(movimiento.descripcion or "—", 34), 8.5)
            self._pagina.texto(318, texto_y, "Ingreso" if ingreso else "Gasto", 8.5,
                               color=ColoresPdf.VERDE if ingreso else ColoresPdf.ROJO)
            self._pagina.texto(370, texto_y, movimiento.moneda, 8.5)
            self._pagina.texto_derecha(470, texto_y, "{} {:,.2f}".format(simbolo, movimiento.monto), 8.5)
            self._pagina.texto_derecha(ANCHO - MARGEN - 4, texto_y, soles(movimiento.monto_en_soles), 8.5, negrita=True)
            self._y -= ALTO_FILA

    def _dibujar_cabecera_tabla(self):
        self._pagina.rectangulo(MARGEN, self._y - ALTO_FILA - 2, ANCHO - 2 * MARGEN, ALTO_FILA + 2, ColoresPdf.MORADO)
        texto_y = self._y - 12.5
        for nombre, x in COLUMNAS:
            self._pagina.texto(x + (4 if x == MARGEN else 0), texto_y, nombre, 8.5, negrita=True, color=ColoresPdf.BLANCO)
        self._pagina.texto_derecha(470, texto_y, "Monto", 8.5, negrita=True, color=ColoresPdf.BLANCO)
        self._pagina.texto_derecha(ANCHO - MARGEN - 4, texto_y, "Monto (PEN)", 8.5, negrita=True, color=ColoresPdf.BLANCO)
        self._y -= ALTO_FILA + 2

    def _numerar_paginas(self):
        total = len(self._documento.paginas)
        for numero, pagina in enumerate(self._documento.paginas, 1):
            pagina.linea(MARGEN, 40, ANCHO - MARGEN, 40)
            pagina.texto(MARGEN, 28, "Kyzen  ·  Reporte financiero", 8, color=ColoresPdf.GRIS)
            pagina.texto_derecha(ANCHO - MARGEN, 28, f"Página {numero} de {total}", 8, color=ColoresPdf.GRIS)

    def _recortar(self, texto, maximo):
        texto = str(texto)
        return texto if len(texto) <= maximo else texto[: maximo - 1] + "…"

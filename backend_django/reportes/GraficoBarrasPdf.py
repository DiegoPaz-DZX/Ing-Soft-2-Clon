from .ColoresPdf import ColoresPdf

DIVISIONES = 4
ESPACIO_ETIQUETAS = 58


class GraficoBarrasPdf:
    def dibujar(self, pagina, x, y, ancho, alto, periodos):
        maximo = max([max(p.ingresos, p.gastos) for p in periodos] + [1])
        escala = float(maximo) * 1.15
        x_area = x + ESPACIO_ETIQUETAS
        ancho_area = ancho - ESPACIO_ETIQUETAS
        y_area = y + 18
        alto_area = alto - 34

        for division in range(DIVISIONES + 1):
            y_linea = y_area + alto_area * division / DIVISIONES
            pagina.linea(x_area, y_linea, x_area + ancho_area, y_linea)
            valor = escala * division / DIVISIONES
            pagina.texto_derecha(x_area - 6, y_linea - 3, "S/ {:,.0f}".format(valor), 7, color=ColoresPdf.GRIS)

        ancho_grupo = ancho_area / len(periodos)
        ancho_barra = min(24, ancho_grupo * 0.32)
        for indice, periodo in enumerate(periodos):
            centro = x_area + ancho_grupo * (indice + 0.5)
            for desplazamiento, monto, color in (
                (-ancho_barra - 1, periodo.ingresos, ColoresPdf.VERDE),
                (1, periodo.gastos, ColoresPdf.ROJO),
            ):
                alto_barra = alto_area * float(monto) / escala
                if alto_barra > 0:
                    pagina.rectangulo(centro + desplazamiento, y_area, ancho_barra, alto_barra, color)
            pagina.texto_centrado(centro, y + 4, self._etiqueta_corta(periodo.etiqueta), 7.5, color=ColoresPdf.GRIS)

        y_leyenda = y + alto - 8
        for desplazamiento, nombre, color in ((0, "Ingresos", ColoresPdf.VERDE), (70, "Gastos", ColoresPdf.ROJO)):
            x_leyenda = x + ancho - 130 + desplazamiento
            pagina.rectangulo(x_leyenda, y_leyenda, 8, 8, color)
            pagina.texto(x_leyenda + 12, y_leyenda + 1, nombre, 8, color=ColoresPdf.TINTA)

    def _etiqueta_corta(self, etiqueta):
        mes, anio = etiqueta.rsplit(" ", 1)
        return f"{mes[:3]} {anio}"

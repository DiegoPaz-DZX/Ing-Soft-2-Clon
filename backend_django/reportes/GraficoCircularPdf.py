from .ColoresPdf import ColoresPdf

ALTO_FILA_LEYENDA = 17


class GraficoCircularPdf:
    def dibujar(self, pagina, cx, cy, radio, categorias, x_leyenda, y_leyenda, x_fin_leyenda):
        angulo = 90.0
        for indice, categoria in enumerate(categorias):
            recorrido = 360.0 * float(categoria.porcentaje) / 100
            color = self._color(indice)
            if recorrido > 0:
                pagina.sector(cx, cy, radio, angulo, angulo - recorrido, color)
            angulo -= recorrido
        pagina.circulo(cx, cy, radio * 0.55, ColoresPdf.BLANCO)

        for indice, categoria in enumerate(categorias):
            y = y_leyenda - indice * ALTO_FILA_LEYENDA
            pagina.rectangulo(x_leyenda, y, 9, 9, self._color(indice))
            pagina.texto(x_leyenda + 15, y + 1, categoria.nombre, 9.5)
            pagina.texto_derecha(x_fin_leyenda - 52, y + 1, "S/ {:,.2f}".format(categoria.monto), 9.5, negrita=True)
            pagina.texto_derecha(x_fin_leyenda, y + 1, f"{categoria.porcentaje}%", 9.5, color=ColoresPdf.GRIS)

    def alto_leyenda(self, categorias):
        return len(categorias) * ALTO_FILA_LEYENDA

    def _color(self, indice):
        return ColoresPdf.CATEGORIAS[indice % len(ColoresPdf.CATEGORIAS)]

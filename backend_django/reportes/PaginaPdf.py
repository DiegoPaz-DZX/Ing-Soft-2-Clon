import math

from .ColoresPdf import ColoresPdf

ANCHOS_ESPECIALES = {
    " ": 278, ",": 278, ".": 278, ":": 278, ";": 278, "/": 278, "'": 191, "-": 333,
    "(": 333, ")": 333, "+": 584, "%": 889, "$": 556, "f": 278, "i": 222, "j": 222,
    "l": 222, "r": 333, "t": 278, "m": 833, "w": 722,
}


class PaginaPdf:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self._operaciones = []

    @staticmethod
    def ancho_texto(texto, tamano, negrita=False):
        total = 0
        for caracter in str(texto):
            if caracter in ANCHOS_ESPECIALES:
                total += ANCHOS_ESPECIALES[caracter]
            elif caracter.isupper():
                total += 667
            else:
                total += 556
        factor = 1.06 if negrita else 1.0
        return total * tamano * factor / 1000

    def texto(self, x, y, texto, tamano=10, negrita=False, color=ColoresPdf.TINTA):
        fuente = "F2" if negrita else "F1"
        self._operaciones.append(
            f"{self._relleno(color)} BT /{fuente} {tamano} Tf {x:.2f} {y:.2f} Td ({self._escapar(texto)}) Tj ET"
        )

    def texto_derecha(self, x_derecha, y, texto, tamano=10, negrita=False, color=ColoresPdf.TINTA):
        self.texto(x_derecha - self.ancho_texto(texto, tamano, negrita), y, texto, tamano, negrita, color)

    def texto_centrado(self, x_centro, y, texto, tamano=10, negrita=False, color=ColoresPdf.TINTA):
        self.texto(x_centro - self.ancho_texto(texto, tamano, negrita) / 2, y, texto, tamano, negrita, color)

    def rectangulo(self, x, y, ancho, alto, color):
        self._operaciones.append(f"{self._relleno(color)} {x:.2f} {y:.2f} {ancho:.2f} {alto:.2f} re f")

    def borde(self, x, y, ancho, alto, color=ColoresPdf.LINEA, grosor=0.6):
        self._operaciones.append(f"{self._trazo(color)} {grosor} w {x:.2f} {y:.2f} {ancho:.2f} {alto:.2f} re S")

    def linea(self, x1, y1, x2, y2, color=ColoresPdf.LINEA, grosor=0.6):
        self._operaciones.append(f"{self._trazo(color)} {grosor} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S")

    def sector(self, cx, cy, radio, grados_inicio, grados_fin, color):
        inicio = math.radians(grados_inicio)
        fin = math.radians(grados_fin)
        partes = max(1, math.ceil(abs(fin - inicio) / (math.pi / 2)))
        paso = (fin - inicio) / partes
        x0, y0 = cx + radio * math.cos(inicio), cy + radio * math.sin(inicio)
        trazos = [f"{cx:.2f} {cy:.2f} m", f"{x0:.2f} {y0:.2f} l"]
        for numero in range(partes):
            a1 = inicio + numero * paso
            a2 = a1 + paso
            k = 4 / 3 * math.tan((a2 - a1) / 4)
            c1x = cx + radio * (math.cos(a1) - k * math.sin(a1))
            c1y = cy + radio * (math.sin(a1) + k * math.cos(a1))
            c2x = cx + radio * (math.cos(a2) + k * math.sin(a2))
            c2y = cy + radio * (math.sin(a2) - k * math.cos(a2))
            x2, y2 = cx + radio * math.cos(a2), cy + radio * math.sin(a2)
            trazos.append(f"{c1x:.2f} {c1y:.2f} {c2x:.2f} {c2y:.2f} {x2:.2f} {y2:.2f} c")
        self._operaciones.append(f"{self._relleno(color)} " + " ".join(trazos) + " h f")

    def circulo(self, cx, cy, radio, color):
        self.sector(cx, cy, radio, 0, 360, color)

    def contenido(self):
        return "\n".join(self._operaciones)

    def _relleno(self, color):
        return "{:.3f} {:.3f} {:.3f} rg".format(*color)

    def _trazo(self, color):
        return "{:.3f} {:.3f} {:.3f} RG".format(*color)

    def _escapar(self, texto):
        bytes_texto = str(texto).encode("cp1252", "replace").decode("latin-1")
        return bytes_texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

from .PaginaPdf import PaginaPdf

FUENTE_NORMAL = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
FUENTE_NEGRITA = "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>"


class DocumentoPdf:
    def __init__(self, ancho, alto):
        self.ancho = ancho
        self.alto = alto
        self.paginas = []

    def nueva_pagina(self):
        pagina = PaginaPdf(self.ancho, self.alto)
        self.paginas.append(pagina)
        return pagina

    def generar(self):
        objetos = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"",
            FUENTE_NORMAL.encode("latin-1"),
            FUENTE_NEGRITA.encode("latin-1"),
        ]
        hijos = []
        for pagina in self.paginas:
            numero_pagina = len(objetos) + 1
            numero_contenido = numero_pagina + 1
            hijos.append(f"{numero_pagina} 0 R")
            objetos.append(
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.ancho:.2f} {self.alto:.2f}] "
                    f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {numero_contenido} 0 R >>"
                ).encode("latin-1")
            )
            contenido = pagina.contenido().encode("latin-1")
            objetos.append(
                f"<< /Length {len(contenido)} >>\nstream\n".encode("latin-1") + contenido + b"\nendstream"
            )
        objetos[1] = f"<< /Type /Pages /Kids [{' '.join(hijos)}] /Count {len(hijos)} >>".encode("latin-1")

        salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        posiciones = []
        for numero, objeto in enumerate(objetos, 1):
            posiciones.append(len(salida))
            salida += f"{numero} 0 obj\n".encode("latin-1") + objeto + b"\nendobj\n"

        inicio_xref = len(salida)
        salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode("latin-1")
        for posicion in posiciones:
            salida += f"{posicion:010d} 00000 n \n".encode("latin-1")
        salida += (
            f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{inicio_xref}\n%%EOF\n"
        ).encode("latin-1")
        return bytes(salida)

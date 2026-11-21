"""Pruebas de Eduardo para la sección 10 del informe (HU20).

Incluye:
- caja blanca de ServicioImportacionMovimientos.importar (V(G) = 10),
- caja negra de POST /api/movimientos/importar,
- prueba unitaria de FabricaLectoresMovimientos.crear.

Si se ejecuta con KYZEN_REPORTE=1 también imprime una línea por caso para
copiar los resultados al informe sin cambiar la lógica de las pruebas.
"""

from io import BytesIO
import os
from types import SimpleNamespace

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from openpyxl import Workbook

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .FabricaLectoresMovimientos import FabricaLectoresMovimientos
from .LectorCsv import LectorCsv
from .LectorExcel import LectorExcel
from .Movimiento import Movimiento
from .RepositorioMovimientos import RepositorioMovimientos
from .ServicioImportacionMovimientos import ServicioImportacionMovimientos
from .ServicioMovimientos import ServicioMovimientos


REPORTE = os.environ.get("KYZEN_REPORTE") == "1"
URL = "/api/movimientos/importar"


def mostrar(caso, entrada, esperado, obtenido):
    if REPORTE:
        print(f"REPORTE|{caso}|{entrada}|{esperado}|{obtenido}")


class RepositorioFalso(RepositorioMovimientos):
    def __init__(self):
        self.movimientos = []

    def agregar(self, movimiento):
        self.movimientos.append(movimiento)

    def sumar_por_tipo(self, *args, **kwargs):
        return 0

    def sumar_gasto_categoria_mes(self, *args, **kwargs):
        return 0

    def eliminar(self, *args, **kwargs):
        return False

    def obtener_por_id(self, *args, **kwargs):
        return None

    def actualizar(self, movimiento):
        return movimiento


def crear_servicio_falso():
    repositorio = RepositorioFalso()
    servicio = ServicioImportacionMovimientos(
        repositorio,
        ServicioMovimientos(repositorio),
    )
    return servicio, repositorio


def cuenta_sin_guardar():
    return CuentaUsuario(id=1, correo="edu@correo.com", clave_hash="hash")


class ImportarMovimientosCajaBlancaTests(SimpleTestCase):
    """V(G)=10 según Radon: se prueban diez caminos representativos."""

    def intentar(self, caso, entrada, archivo):
        servicio, repositorio = crear_servicio_falso()
        try:
            resultado = servicio.importar(cuenta_sin_guardar(), archivo)
            obtenido = f"OK importados={len(resultado)}"
        except ArchivoImportacionInvalidoException as error:
            resultado = None
            obtenido = f"Error: {error}"
        mostrar(caso, entrada, "según camino", obtenido)
        return resultado, obtenido, repositorio

    def test_cb01_archivo_ausente(self):
        _, obtenido, _ = self.intentar("CB-01", "archivo=None", None)
        self.assertEqual(obtenido, "Error: Selecciona un archivo para importar.")

    def test_cb02_archivo_mayor_a_cinco_mb(self):
        archivo = SimpleNamespace(
            name="movimientos.csv",
            size=ServicioImportacionMovimientos.TAMANO_MAXIMO + 1,
        )
        _, obtenido, _ = self.intentar("CB-02", "tamaño=5 MB + 1 byte", archivo)
        self.assertEqual(obtenido, "Error: El archivo no puede superar los 5 MB.")

    def test_cb03_archivo_sin_movimientos(self):
        archivo = SimpleUploadedFile("movimientos.csv", b"tipo,monto,fecha\n")
        _, obtenido, _ = self.intentar("CB-03", "solo encabezados", archivo)
        self.assertEqual(obtenido, "Error: El archivo no contiene movimientos.")

    def test_cb04_mas_de_quinientas_filas(self):
        filas = ["tipo,monto,fecha"] + [
            f"ingreso,{numero + 1},2026-11-01" for numero in range(501)
        ]
        archivo = SimpleUploadedFile(
            "movimientos.csv", ("\n".join(filas) + "\n").encode("utf-8")
        )
        _, obtenido, _ = self.intentar("CB-04", "501 filas", archivo)
        self.assertEqual(
            obtenido,
            "Error: Solo se pueden importar 500 movimientos a la vez.",
        )

    def test_cb05_ingreso_valido_no_pasa_por_categoria(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            b"tipo,monto,fecha,descripcion\ningreso,100,2026-11-01,Sueldo\n",
        )
        resultado, obtenido, repositorio = self.intentar("CB-05", "ingreso válido", archivo)
        self.assertEqual(obtenido, "OK importados=1")
        self.assertEqual(len(resultado), 1)
        self.assertEqual(len(repositorio.movimientos), 1)

    def test_cb06_gasto_valido_con_categoria(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            b"tipo,monto,fecha,categoria\ngasto,25,2026-11-01,alimentacion\n",
        )
        _, obtenido, repositorio = self.intentar("CB-06", "gasto con categoría", archivo)
        self.assertEqual(obtenido, "OK importados=1")
        self.assertEqual(repositorio.movimientos[0].categoria, "alimentacion")

    def test_cb07_gasto_sin_categoria(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            b"tipo,monto,fecha,categoria\ngasto,25,2026-11-01,\n",
        )
        _, obtenido, repositorio = self.intentar("CB-07", "gasto sin categoría", archivo)
        self.assertIn("Hay filas que deben corregirse", obtenido)
        self.assertEqual(repositorio.movimientos, [])

    def test_cb08_monto_invalido_entra_al_except(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            b"tipo,monto,fecha\ningreso,-10,2026-11-01\n",
        )
        _, obtenido, repositorio = self.intentar("CB-08", "monto=-10", archivo)
        self.assertIn("Hay filas que deben corregirse", obtenido)
        self.assertEqual(repositorio.movimientos, [])

    def test_cb09_una_fila_valida_y_otra_invalida_no_guardan_parcial(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,categoria\n"
                "gasto,20,2026-11-01,alimentacion\n"
                "gasto,0,2026-11-02,transporte\n"
            ).encode("utf-8"),
        )
        _, obtenido, repositorio = self.intentar("CB-09", "fila válida + fila inválida", archivo)
        self.assertIn("Hay filas que deben corregirse", obtenido)
        self.assertEqual(repositorio.movimientos, [])

    def test_cb10_dos_filas_validas_llegan_al_guardado(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,descripcion,categoria,moneda\n"
                "ingreso,900,2026-11-01,Prácticas,,PEN\n"
                "gasto,22,2026-11-02,Almuerzo,alimentacion,USD\n"
            ).encode("utf-8"),
        )
        resultado, obtenido, repositorio = self.intentar("CB-10", "dos filas válidas", archivo)
        self.assertEqual(obtenido, "OK importados=2")
        self.assertEqual(len(resultado), 2)
        self.assertEqual(len(repositorio.movimientos), 2)


def crear_cuenta(correo):
    cuenta = CuentaUsuario(correo=correo)
    cuenta.definir_clave("Kyzen2026")
    cuenta.save()
    return cuenta


class ImportacionCajaNegraTests(TestCase):
    """Particiones del archivo, sus seis campos lógicos y la sesión."""

    def setUp(self):
        self.cuenta = crear_cuenta("edu@correo.com")
        self.otra_cuenta = crear_cuenta("otra@correo.com")
        self.token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)

    def enviar(self, archivo=None, token=True):
        cabecera = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"} if token else {}
        datos = {"archivo": archivo} if archivo is not None else {}
        return self.client.post(URL, datos, **cabecera)

    def caso(self, caso, entrada, esperado, archivo=None, token=True):
        respuesta = self.enviar(archivo, token)
        cuerpo = respuesta.json()
        obtenido = f"{respuesta.status_code}"
        if "error" in cuerpo:
            obtenido += f" {cuerpo['error']}"
        mostrar(caso, entrada, esperado, obtenido)
        return respuesta, cuerpo

    def test_cn01_csv_valido(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,descripcion,categoria,moneda\n"
                "ingreso,900,2026-11-01,Prácticas,,PEN\n"
                "gasto,22,2026-11-02,Almuerzo,alimentacion,PEN\n"
            ).encode("utf-8"),
            content_type="text/csv",
        )
        respuesta, cuerpo = self.caso("CN-01", "CSV válido con token", "201", archivo)
        self.assertEqual((respuesta.status_code, cuerpo["importados"]), (201, 2))
        self.assertEqual(Movimiento.objects.filter(usuario=self.cuenta).count(), 2)
        self.assertEqual(Movimiento.objects.filter(usuario=self.otra_cuenta).count(), 0)

    def test_cn02_xlsx_valido(self):
        libro = Workbook()
        hoja = libro.active
        hoja.append(["tipo", "monto", "fecha", "descripcion", "categoria", "moneda"])
        hoja.append(["gasto", 18.5, "2026-11-03", "Pasaje", "transporte", "PEN"])
        contenido = BytesIO()
        libro.save(contenido)
        archivo = SimpleUploadedFile(
            "movimientos.xlsx",
            contenido.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        respuesta, cuerpo = self.caso("CN-02", "XLSX válido con token", "201", archivo)
        self.assertEqual((respuesta.status_code, cuerpo["importados"]), (201, 1))

    def test_cn03_sin_token(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv", b"tipo,monto,fecha\ningreso,10,2026-11-01\n"
        )
        respuesta, _ = self.caso("CN-03", "CSV válido sin token", "401", archivo, token=False)
        self.assertEqual(respuesta.status_code, 401)

    def test_cn04_sin_archivo(self):
        respuesta, cuerpo = self.caso("CN-04", "petición sin archivo", "400")
        self.assertEqual((respuesta.status_code, cuerpo["error"]), (400, "Selecciona un archivo para importar."))

    def test_cn05_extension_no_permitida(self):
        archivo = SimpleUploadedFile("movimientos.txt", b"tipo,monto,fecha")
        respuesta, cuerpo = self.caso("CN-05", "archivo TXT", "400", archivo)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("CSV, XLS o XLSX", cuerpo["error"])

    def test_cn06_faltan_columnas_obligatorias(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv", b"descripcion,categoria\nAlmuerzo,alimentacion\n"
        )
        respuesta, cuerpo = self.caso("CN-06", "CSV sin tipo, monto ni fecha", "400", archivo)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("Faltan las columnas", cuerpo["error"])

    def test_cn07_monto_cero_no_guarda_datos(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,categoria\n"
                "gasto,20,2026-11-01,alimentacion\n"
                "gasto,0,2026-11-02,transporte\n"
            ).encode("utf-8"),
        )
        respuesta, cuerpo = self.caso("CN-07", "segunda fila con monto cero", "400", archivo)
        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(cuerpo["errores"][0]["fila"], 3)
        self.assertEqual(Movimiento.objects.count(), 0)

    def test_cn08_archivo_mayor_a_cinco_mb(self):
        archivo = SimpleUploadedFile("grande.csv", b"0" * (5 * 1024 * 1024 + 1))
        respuesta, cuerpo = self.caso("CN-08", "archivo de 5 MB + 1 byte", "400", archivo)
        self.assertEqual((respuesta.status_code, cuerpo["error"]), (400, "El archivo no puede superar los 5 MB."))

    def test_cn09_mas_de_quinientas_filas(self):
        filas = ["tipo,monto,fecha"] + [
            f"ingreso,{numero + 1},2026-11-01" for numero in range(501)
        ]
        archivo = SimpleUploadedFile(
            "movimientos.csv", ("\n".join(filas) + "\n").encode("utf-8")
        )
        respuesta, cuerpo = self.caso("CN-09", "CSV con 501 filas", "400", archivo)
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("500 movimientos", cuerpo["error"])


class FabricaLectoresPruebaUnitariaTests(SimpleTestCase):
    def comprobar(self, caso, nombre, esperado):
        try:
            lector = FabricaLectoresMovimientos.crear(nombre)
            obtenido = type(lector).__name__
        except ArchivoImportacionInvalidoException as error:
            lector = None
            obtenido = f"Error: {error}"
        mostrar(caso, f"nombre={nombre}", esperado, obtenido)
        return lector, obtenido

    def test_ut01_csv_crea_lector_csv(self):
        lector, _ = self.comprobar("UT-01", "datos.csv", "LectorCsv")
        self.assertIsInstance(lector, LectorCsv)

    def test_ut02_xls_crea_lector_excel(self):
        lector, _ = self.comprobar("UT-02", "datos.xls", "LectorExcel")
        self.assertIsInstance(lector, LectorExcel)

    def test_ut03_xlsx_crea_lector_excel(self):
        lector, _ = self.comprobar("UT-03", "datos.xlsx", "LectorExcel")
        self.assertIsInstance(lector, LectorExcel)

    def test_ut04_extension_invalida_lanza_excepcion(self):
        lector, obtenido = self.comprobar("UT-04", "datos.pdf", "Error controlado")
        self.assertIsNone(lector)
        self.assertIn("CSV, XLS o XLSX", obtenido)

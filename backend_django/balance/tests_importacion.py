from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase
from openpyxl import Workbook

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RepositorioCuentasDjango import RepositorioCuentasDjango
from usuarios.ServicioTokens import ServicioTokens

from .ArchivoImportacionInvalidoException import ArchivoImportacionInvalidoException
from .Movimiento import Movimiento
from .RepositorioMovimientos import RepositorioMovimientos
from .ServicioImportacionMovimientos import ServicioImportacionMovimientos
from .ServicioMovimientos import ServicioMovimientos


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


def cuenta_sin_guardar(cuenta_id=1):
    return CuentaUsuario(id=cuenta_id, correo=f"usuario{cuenta_id}@correo.com", clave_hash="hash")


class ServicioImportacionMovimientosTests(SimpleTestCase):
    def test_importa_csv_y_asigna_la_cuenta(self):
        servicio, repositorio = crear_servicio_falso()
        cuenta = cuenta_sin_guardar()
        contenido = (
            "tipo,monto,fecha,descripcion,categoria,moneda\n"
            "ingreso,1200,2026-11-01,Sueldo,,PEN\n"
            "gasto,35.50,2026-11-02,Almuerzo,alimentacion,USD\n"
        )
        archivo = SimpleUploadedFile("movimientos.csv", contenido.encode("utf-8"))

        resultado = servicio.importar(cuenta, archivo)

        self.assertEqual(len(resultado), 2)
        self.assertEqual(len(repositorio.movimientos), 2)
        self.assertIs(repositorio.movimientos[0].usuario, cuenta)
        self.assertEqual(repositorio.movimientos[1].categoria, "alimentacion")
        self.assertEqual(repositorio.movimientos[1].moneda, "USD")

    def test_importa_excel_xlsx(self):
        servicio, repositorio = crear_servicio_falso()
        libro = Workbook()
        hoja = libro.active
        hoja.append(["tipo", "monto", "fecha", "descripcion", "categoria", "moneda"])
        hoja.append(["gasto", 18.5, "2026-11-03", "Pasaje", "transporte", "PEN"])
        contenido = BytesIO()
        libro.save(contenido)
        archivo = SimpleUploadedFile("movimientos.xlsx", contenido.getvalue())

        servicio.importar(cuenta_sin_guardar(), archivo)

        self.assertEqual(len(repositorio.movimientos), 1)
        self.assertEqual(repositorio.movimientos[0].descripcion, "Pasaje")

    def test_no_guarda_nada_si_una_fila_tiene_error(self):
        servicio, repositorio = crear_servicio_falso()
        contenido = (
            "tipo,monto,fecha,categoria\n"
            "gasto,20,2026-11-01,alimentacion\n"
            "gasto,-5,2026-11-02,transporte\n"
        )
        archivo = SimpleUploadedFile("movimientos.csv", contenido.encode("utf-8"))

        with self.assertRaises(ArchivoImportacionInvalidoException) as contexto:
            servicio.importar(cuenta_sin_guardar(), archivo)

        self.assertEqual(repositorio.movimientos, [])
        self.assertEqual(contexto.exception.errores[0]["fila"], 3)

    def test_rechaza_archivo_sin_columnas_obligatorias(self):
        servicio, _ = crear_servicio_falso()
        archivo = SimpleUploadedFile(
            "movimientos.csv", b"descripcion,categoria\nAlmuerzo,alimentacion\n"
        )

        with self.assertRaisesRegex(ArchivoImportacionInvalidoException, "Faltan las columnas"):
            servicio.importar(cuenta_sin_guardar(), archivo)

    def test_rechaza_una_extension_no_permitida(self):
        servicio, _ = crear_servicio_falso()
        archivo = SimpleUploadedFile("movimientos.txt", b"tipo,monto,fecha")

        with self.assertRaisesRegex(ArchivoImportacionInvalidoException, "CSV, XLS o XLSX"):
            servicio.importar(cuenta_sin_guardar(), archivo)


def crear_cuenta(correo):
    cuenta = CuentaUsuario(correo=correo)
    cuenta.definir_clave("Kyzen2026")
    cuenta.save()
    return cuenta


class ImportacionEndpointTests(TestCase):
    def setUp(self):
        self.cuenta = crear_cuenta("edu@correo.com")
        self.otra_cuenta = crear_cuenta("otra@correo.com")
        self.token = ServicioTokens(RepositorioCuentasDjango()).crear(self.cuenta)

    def test_importa_los_movimientos_solo_en_la_cuenta_de_la_sesion(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,descripcion,categoria,moneda\n"
                "ingreso,900,2026-11-01,Prácticas,,PEN\n"
                "gasto,22,2026-11-02,Almuerzo,alimentacion,PEN\n"
            ).encode("utf-8"),
            content_type="text/csv",
        )

        respuesta = self.client.post(
            "/api/movimientos/importar",
            {"archivo": archivo},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )

        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.json()["importados"], 2)
        self.assertEqual(Movimiento.objects.filter(usuario=self.cuenta).count(), 2)
        self.assertEqual(Movimiento.objects.filter(usuario=self.otra_cuenta).count(), 0)

    def test_rechaza_la_importacion_sin_sesion(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv", b"tipo,monto,fecha\ningreso,10,2026-11-01\n"
        )

        respuesta = self.client.post("/api/movimientos/importar", {"archivo": archivo})

        self.assertEqual(respuesta.status_code, 401)

    def test_devuelve_los_errores_de_fila_sin_guardar_datos(self):
        archivo = SimpleUploadedFile(
            "movimientos.csv",
            (
                "tipo,monto,fecha,categoria\n"
                "gasto,20,2026-11-01,alimentacion\n"
                "gasto,0,2026-11-02,transporte\n"
            ).encode("utf-8"),
        )

        respuesta = self.client.post(
            "/api/movimientos/importar",
            {"archivo": archivo},
            HTTP_AUTHORIZATION=f"Bearer {self.token}",
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(respuesta.json()["errores"][0]["fila"], 3)
        self.assertEqual(Movimiento.objects.count(), 0)

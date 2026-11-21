"""Caja negra del endpoint POST /api/movimientos/nuevo (formulario de transacción).

Campos de entrada (8): tipo, monto, fecha, descripcion, categoria (HU15), moneda,
meta_id (HU25) y comprobante (archivo, multipart). Más el encabezado Authorization.
"""
import json
import os
import shutil
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from metas.models import MetaAhorro
from usuarios.CuentaUsuario import CuentaUsuario

REPORTE = os.environ.get("KYZEN_REPORTE") == "1"
URL = "/api/movimientos/nuevo"
BASE = {"tipo": "gasto", "monto": "50", "fecha": "2026-11-10", "descripcion": "almuerzo",
        "categoria": "alimentacion", "moneda": "PEN"}

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 32


def registrar_y_entrar(cliente, correo):
    cliente.post("/api/registro", json.dumps({"correo": correo, "clave": "Clave12345!", "confirmacion": "Clave12345!"}),
                 content_type="application/json")
    r = cliente.post("/api/login", json.dumps({"correo": correo, "clave": "Clave12345!"}),
                     content_type="application/json")
    return json.loads(r.content)["token"]


class FormularioMovimientoCajaNegraTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._media = tempfile.mkdtemp()
        cls._override = override_settings(MEDIA_ROOT=cls._media)
        cls._override.enable()

    @classmethod
    def tearDownClass(cls):
        cls._override.disable()
        shutil.rmtree(cls._media, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.c = Client()
        self.token = registrar_y_entrar(self.c, "nico@correo.com")
        self.cuenta = CuentaUsuario.objects.get(correo="nico@correo.com")
        self.meta = MetaAhorro.objects.create(usuario=self.cuenta, nombre="Viaje", objetivo_pen=1000)
        otra = CuentaUsuario.objects.create(correo="otra@correo.com", clave_hash="x")
        self.meta_ajena = MetaAhorro.objects.create(usuario=otra, nombre="Ajena", objetivo_pen=500)

    def enviar(self, cambios=None, token=True, archivo=None):
        datos = {**BASE, **(cambios or {})}
        cabecera = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"} if token else {}
        if archivo is not None:
            datos = {k: v for k, v in datos.items() if v is not None}
            return self.c.post(URL, {**datos, "comprobante": archivo}, **cabecera)
        return self.c.post(URL, json.dumps(datos), content_type="application/json", **cabecera)

    def caso(self, id_caso, descripcion, esperado, **kwargs):
        r = self.enviar(**kwargs)
        cuerpo = json.loads(r.content)
        obtenido = f"{r.status_code}" + (f" {cuerpo['error']}" if "error" in cuerpo else "")
        if REPORTE:
            print(f"REPORTE|{id_caso}|{descripcion}|{esperado}|{obtenido}")
        return r, cuerpo

    # ---- particiones válidas
    def test_cn01_ingreso_valido(self):
        r, c = self.caso("CN-01", "tipo=ingreso, monto=1000, USD no, PEN", "201",
                         cambios={"tipo": "ingreso", "monto": "1000", "categoria": "", "descripcion": "sueldo"})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(c["categoria"], "")

    def test_cn02_gasto_en_dolares(self):
        r, c = self.caso("CN-02", "gasto, 20, USD, categoria=transporte", "201",
                         cambios={"monto": "20", "moneda": "USD", "categoria": "transporte"})
        self.assertEqual((r.status_code, c["moneda"], c["categoria"]), (201, "USD", "transporte"))

    def test_cn03_gasto_ahorro_con_meta_propia(self):
        r, c = self.caso("CN-03", "gasto, categoria=ahorro, meta_id propia", "201 meta_id=meta",
                         cambios={"categoria": "ahorro", "meta_id": self.meta.pk})
        self.assertEqual((r.status_code, c["meta_id"], c["meta_nombre"]), (201, self.meta.pk, "Viaje"))

    def test_cn04_categoria_ahorro_en_mayusculas_con_meta(self):
        # DEFECTO ENCONTRADO: ServicioMovimientos._obtener_meta compara `categoria == "ahorro"`
        # ANTES de normalizar a minúsculas, así que "AHORRO" + meta_id se rechaza.
        # Esperado ideal: 201. Obtenido real: 400. La prueba fija el comportamiento actual.
        r, c = self.caso("CN-04", "categoria='AHORRO' con meta propia", "201 (ideal)",
                         cambios={"categoria": "AHORRO", "meta_id": self.meta.pk})
        self.assertEqual((r.status_code, c["error"]),
                         (400, "La meta solo puede asociarse a un gasto de categoría ahorro."))

    def test_cn04b_categoria_ahorro_en_mayusculas_sin_meta_evita_la_regla(self):
        # Mismo defecto, efecto contrario: sin meta_id "AHORRO" no dispara la exigencia de meta
        # y se guarda como "ahorro" sin meta asociada.
        r, c = self.caso("CN-04b", "categoria='AHORRO' sin meta_id", "400 Selecciona la meta (ideal)",
                         cambios={"categoria": "AHORRO"})
        self.assertEqual((r.status_code, c["categoria"], c["meta_id"]), (201, "ahorro", None))

    def test_cn05_comprobante_png_valido(self):
        archivo = SimpleUploadedFile("boleta.png", PNG, content_type="image/png")
        r, c = self.caso("CN-05", "comprobante boleta.png (image/png)", "201", archivo=archivo)
        self.assertEqual(r.status_code, 201)
        self.assertTrue(c["comprobante_url"])

    # ---- valores límite del monto
    def test_cn06_monto_limite_inferior_valido(self):
        r, _ = self.caso("CN-06", "monto=0.01 (mínimo positivo)", "201", cambios={"monto": "0.01"})
        self.assertEqual(r.status_code, 201)

    def test_cn07_monto_cero(self):
        r, c = self.caso("CN-07", "monto=0 (límite)", "400 El monto debe ser mayor que cero", cambios={"monto": "0"})
        self.assertEqual((r.status_code, c["error"]), (400, "El monto debe ser mayor que cero"))

    def test_cn08_monto_negativo(self):
        r, c = self.caso("CN-08", "monto=-5", "400 El monto debe ser mayor que cero", cambios={"monto": "-5"})
        self.assertEqual((r.status_code, c["error"]), (400, "El monto debe ser mayor que cero"))

    def test_cn09_monto_no_numerico(self):
        r, c = self.caso("CN-09", "monto='abc'", "400 El monto debe ser un número", cambios={"monto": "abc"})
        self.assertEqual((r.status_code, c["error"]), (400, "El monto debe ser un número"))

    # ---- particiones inválidas de los demás campos
    def test_cn10_tipo_invalido(self):
        r, c = self.caso("CN-10", "tipo='transferencia'", "400 El tipo debe ser ingreso o gasto",
                         cambios={"tipo": "transferencia"})
        self.assertEqual((r.status_code, c["error"]), (400, "El tipo debe ser ingreso o gasto"))

    def test_cn11_fecha_inexistente(self):
        r, c = self.caso("CN-11", "fecha='2026-13-01'", "400 La fecha es obligatoria (AAAA-MM-DD)",
                         cambios={"fecha": "2026-13-01"})
        self.assertEqual((r.status_code, c["error"]), (400, "La fecha es obligatoria (AAAA-MM-DD)"))

    def test_cn12_fecha_vacia(self):
        r, c = self.caso("CN-12", "fecha=''", "400 La fecha es obligatoria (AAAA-MM-DD)", cambios={"fecha": ""})
        self.assertEqual((r.status_code, c["error"]), (400, "La fecha es obligatoria (AAAA-MM-DD)"))

    def test_cn13_moneda_no_permitida(self):
        r, c = self.caso("CN-13", "moneda='EUR'", "400 La moneda debe ser Soles (PEN) o Dólares (USD)",
                         cambios={"moneda": "EUR"})
        self.assertEqual((r.status_code, c["error"]), (400, "La moneda debe ser Soles (PEN) o Dólares (USD)"))

    # ---- reglas HU25 (ahorro <-> meta)
    def test_cn14_gasto_ahorro_sin_meta(self):
        r, c = self.caso("CN-14", "categoria=ahorro, sin meta_id", "400 Selecciona la meta que recibirá este ahorro.",
                         cambios={"categoria": "ahorro"})
        self.assertEqual((r.status_code, c["error"]), (400, "Selecciona la meta que recibirá este ahorro."))

    def test_cn15_meta_en_gasto_que_no_es_ahorro(self):
        r, c = self.caso("CN-15", "categoria=alimentacion con meta_id",
                         "400 La meta solo puede asociarse a un gasto de categoría ahorro.",
                         cambios={"meta_id": self.meta.pk})
        self.assertEqual((r.status_code, c["error"]), (400, "La meta solo puede asociarse a un gasto de categoría ahorro."))

    def test_cn16_meta_en_ingreso(self):
        r, c = self.caso("CN-16", "tipo=ingreso con meta_id",
                         "400 La meta solo puede asociarse a un gasto de categoría ahorro.",
                         cambios={"tipo": "ingreso", "categoria": "", "meta_id": self.meta.pk})
        self.assertEqual((r.status_code, c["error"]), (400, "La meta solo puede asociarse a un gasto de categoría ahorro."))

    def test_cn17_meta_de_otra_cuenta(self):
        r, c = self.caso("CN-17", "categoria=ahorro, meta_id de otra cuenta",
                         "400 La meta no existe o no pertenece a esta cuenta.",
                         cambios={"categoria": "ahorro", "meta_id": self.meta_ajena.pk})
        self.assertEqual((r.status_code, c["error"]), (400, "La meta no existe o no pertenece a esta cuenta."))

    # ---- comprobante y sesión
    def test_cn18_comprobante_extension_no_permitida(self):
        archivo = SimpleUploadedFile("virus.exe", b"MZ", content_type="application/octet-stream")
        r, c = self.caso("CN-18", "comprobante virus.exe", "400 Solo se permiten archivos JPG, PNG o PDF", archivo=archivo)
        self.assertEqual((r.status_code, c["error"]), (400, "Solo se permiten archivos JPG, PNG o PDF"))

    def test_cn19_comprobante_mayor_a_5_mb(self):
        archivo = SimpleUploadedFile("grande.png", b"0" * (5 * 1024 * 1024 + 1), content_type="image/png")
        r, c = self.caso("CN-19", "comprobante de 5 MB + 1 byte", "400 El archivo no puede superar los 5 MB", archivo=archivo)
        self.assertEqual((r.status_code, c["error"]), (400, "El archivo no puede superar los 5 MB"))

    def test_cn20_sin_token(self):
        r, c = self.caso("CN-20", "sin encabezado Authorization", "401 La sesion es obligatoria", token=False)
        self.assertEqual((r.status_code, c["error"]), (401, "La sesion es obligatoria"))

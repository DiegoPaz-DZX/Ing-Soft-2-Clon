from django.test import SimpleTestCase

from .RepositorioTipsMemoria import RepositorioTipsMemoria
from .ServicioTips import ServicioTips


class ServicioTipsTests(SimpleTestCase):
    def test_hay_ocho_tips_numerados_del_1_al_8(self):
        tips = ServicioTips(RepositorioTipsMemoria()).obtener_todos()
        self.assertEqual([tip.numero for tip in tips], list(range(1, 9)))

    def test_cada_tip_tiene_titulo_y_contenido(self):
        for tip in ServicioTips(RepositorioTipsMemoria()).obtener_todos():
            self.assertTrue(tip.titulo)
            self.assertTrue(tip.contenido)

    def test_modificar_la_lista_devuelta_no_cambia_los_tips(self):
        servicio = ServicioTips(RepositorioTipsMemoria())
        servicio.obtener_todos().clear()
        self.assertEqual(len(servicio.obtener_todos()), 8)


class TipsEndpointTests(SimpleTestCase):
    def test_responde_la_lista_de_tips(self):
        respuesta = self.client.get("/api/tips")
        self.assertEqual(respuesta.status_code, 200)
        datos = respuesta.json()
        self.assertEqual(len(datos), 8)
        self.assertEqual(set(datos[0]), {"numero", "titulo", "contenido"})

    def test_las_tildes_llegan_bien(self):
        datos = self.client.get("/api/tips").json()
        self.assertIn("prácticas", datos[0]["contenido"])

    def test_incluye_los_permisos_para_el_frontend(self):
        respuesta = self.client.get("/api/tips")
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")

    def test_solo_acepta_get(self):
        respuesta = self.client.post("/api/tips")
        self.assertEqual(respuesta.status_code, 405)

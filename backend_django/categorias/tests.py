from django.test import SimpleTestCase

from .RepositorioCategorias import RepositorioCategorias
from .RepositorioCategoriasMemoria import RepositorioCategoriasMemoria
from .ServicioCategorias import ServicioCategorias


class RepositorioCategoriasFalso(RepositorioCategorias):
    def listar_todas(self):
        return ["categoria-de-prueba"]


class ServicioCategoriasTests(SimpleTestCase):
    def test_lista_las_ocho_categorias_de_gasto(self):
        categorias = ServicioCategorias(RepositorioCategoriasMemoria()).obtener_todas()
        self.assertEqual(len(categorias), 8)
        self.assertEqual(categorias[1].codigo, "transporte")
        self.assertEqual(categorias[-1].codigo, "otros")

    def test_depende_de_la_interfaz_del_repositorio(self):
        categorias = ServicioCategorias(RepositorioCategoriasFalso()).obtener_todas()
        self.assertEqual(categorias, ["categoria-de-prueba"])


class CategoriasEndpointTests(SimpleTestCase):
    def test_responde_las_categorias_para_el_frontend(self):
        respuesta = self.client.get("/api/categorias")
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 8)
        self.assertEqual(set(respuesta.json()[0]), {"id", "nombre"})

    def test_incluye_cors_y_solo_acepta_get(self):
        respuesta = self.client.get("/api/categorias")
        self.assertEqual(respuesta["Access-Control-Allow-Origin"], "*")
        self.assertEqual(self.client.post("/api/categorias").status_code, 405)

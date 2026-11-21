from datetime import date
from decimal import Decimal
from .GeneradorAlertaAdvertencia import GeneradorAlertaAdvertencia
from .GeneradorAlertaCritica import GeneradorAlertaCritica

class ServicioAlertas:
    def __init__(self, repositorio_limites, repositorio_alertas, repositorio_movimientos):
        self._repositorio_limites = repositorio_limites
        self._repositorio_alertas = repositorio_alertas
        self._repositorio_movimientos = repositorio_movimientos
        # Factory Method: instancia los generadores concretos
        self._generador_advertencia = GeneradorAlertaAdvertencia()
        self._generador_critica = GeneradorAlertaCritica()

    def establecer_limite(self, cuenta, categoria, limite_mensual):
        if not categoria or Decimal(str(limite_mensual)) <= 0:
            raise ValueError("Categoría y límite (mayor a 0) son obligatorios")
        self._repositorio_limites.guardar_limite(str(cuenta.pk), categoria, limite_mensual)

    def generar_alertas(self, cuenta):
        usuario_id = str(cuenta.pk)
        hoy = date.today()
        pendientes = self._repositorio_alertas.obtener_alertas_usuario(usuario_id)
        claves = {(a.categoria, a.tipo_alerta.value) for a in pendientes}

        limites = self._repositorio_limites.obtener_limites_usuario(usuario_id)
        for categoria, limite in limites.items():
            gastado = self._repositorio_movimientos.sumar_gasto_categoria_mes(
                cuenta, categoria, hoy.year, hoy.month
            )
            
            # Factory Method: cada generador crea su tipo de alerta si aplica
            alerta = self._generador_advertencia.crear_alerta(usuario_id, categoria, limite, gastado)
            if alerta and (alerta.categoria, alerta.tipo_alerta.value) not in claves:
                self._repositorio_alertas.guardar_alerta(alerta)
                claves.add((alerta.categoria, alerta.tipo_alerta.value))
            
            alerta = self._generador_critica.crear_alerta(usuario_id, categoria, limite, gastado)
            if alerta and (alerta.categoria, alerta.tipo_alerta.value) not in claves:
                self._repositorio_alertas.guardar_alerta(alerta)
                claves.add((alerta.categoria, alerta.tipo_alerta.value))

        return self._repositorio_alertas.obtener_alertas_usuario(usuario_id)

    def obtener_limites(self, cuenta):
        return self._repositorio_limites.obtener_limites_usuario(str(cuenta.pk))

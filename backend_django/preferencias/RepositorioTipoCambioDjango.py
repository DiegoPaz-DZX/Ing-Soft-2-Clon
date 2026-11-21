from .RepositorioTipoCambio import RepositorioTipoCambio
from .TipoCambio import TipoCambio
from .TipoCambioDiario import TipoCambioDiario


class RepositorioTipoCambioDjango(RepositorioTipoCambio):
    def obtener_de_fecha(self, fecha):
        return self._a_tipo_cambio(TipoCambioDiario.objects.filter(fecha=fecha).first())

    def obtener_ultimo(self):
        return self._a_tipo_cambio(TipoCambioDiario.objects.order_by("-fecha").first())

    def guardar(self, fecha, soles_por_dolar, fuente):
        registro, _ = TipoCambioDiario.objects.update_or_create(
            fecha=fecha, defaults={"soles_por_dolar": soles_por_dolar, "fuente": fuente}
        )
        registro.refresh_from_db()
        return self._a_tipo_cambio(registro)

    def _a_tipo_cambio(self, registro):
        if registro is None:
            return None
        return TipoCambio(registro.fecha, registro.soles_por_dolar, registro.fuente)

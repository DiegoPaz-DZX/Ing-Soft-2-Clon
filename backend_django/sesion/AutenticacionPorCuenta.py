from .EstrategiaAutenticacion import EstrategiaAutenticacion


class AutenticacionPorCuenta(EstrategiaAutenticacion):
    def __init__(self, repositorio_cuentas):
        self._repositorio_cuentas = repositorio_cuentas

    def autenticar(self, correo, clave):
        cuenta = self._repositorio_cuentas.buscar_por_correo(correo)
        if cuenta is None or not cuenta.verificar_clave(clave):
            return None
        return cuenta

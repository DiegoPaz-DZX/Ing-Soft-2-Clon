from .CuentaUsuario import CuentaUsuario
from .RepositorioCuentas import RepositorioCuentas


class RepositorioCuentasDjango(RepositorioCuentas):
    def guardar(self, cuenta):
        cuenta.save()

    def buscar_por_correo(self, correo):
        return CuentaUsuario.objects.filter(correo__iexact=correo).first()

    def buscar_por_id(self, cuenta_id):
        return CuentaUsuario.objects.filter(pk=cuenta_id).first()

    def listar(self):
        return list(CuentaUsuario.objects.order_by("correo"))

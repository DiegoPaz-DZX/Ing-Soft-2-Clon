from django.core.management.base import BaseCommand, CommandError

from usuarios.CuentaUsuario import CuentaUsuario
from usuarios.RolUsuario import RolUsuario


class Command(BaseCommand):
    help = "Crea o actualiza una cuenta administradora para el entorno local"

    def add_arguments(self, parser):
        parser.add_argument("correo")
        parser.add_argument("clave")

    def handle(self, *args, **opciones):
        correo = opciones["correo"].strip().lower()
        clave = opciones["clave"]
        if len(clave) < 8:
            raise CommandError("La contraseña debe tener al menos 8 caracteres.")
        cuenta, _ = CuentaUsuario.objects.get_or_create(correo=correo)
        cuenta.definir_clave(clave)
        cuenta.rol = RolUsuario.ADMINISTRADOR
        cuenta.save()
        self.stdout.write(self.style.SUCCESS(f"Administrador listo: {correo}"))

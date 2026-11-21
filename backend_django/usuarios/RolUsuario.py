from django.db import models


class RolUsuario(models.TextChoices):
    USUARIO = "USUARIO", "Usuario"
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"

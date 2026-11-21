from django.db import migrations
from django.db.models import Model

from balance.Movimiento import Movimiento
from usuarios.CuentaUsuario import CuentaUsuario


def asignar_usuario_default(apps, schema_editor):
    Movimiento = apps.get_model('balance', 'Movimiento')
    CuentaUsuario = apps.get_model('usuarios', 'CuentaUsuario')

    cuenta = CuentaUsuario.objects.order_by('id').first()
    if cuenta is None:
        return

    Movimiento.objects.filter(usuario__isnull = True).update(usuario = cuenta)

class Migration(migrations.Migration):
    dependencies = [
        ('balance', '0006_movimiento_usuario'),
        ('usuarios', '0002_cuentausuario_rol'),
    ]
    operations = [
        migrations.RunPython(asignar_usuario_default)
    ]
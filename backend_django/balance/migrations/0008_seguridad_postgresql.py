from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("balance", "0007_asignar_usuario_movimiento"),
    ]

    operations = [
        migrations.RunPython(migrations.RunPython.noop, migrations.RunPython.noop),
    ]

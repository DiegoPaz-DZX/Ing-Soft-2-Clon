import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0002_cuentausuario_rol")]

    operations = [
        migrations.CreateModel(
            name="CodigoCambioClave",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("codigo_hash", models.CharField(max_length=128)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("expira_en", models.DateTimeField()),
                ("usado", models.BooleanField(default=False)),
                ("intentos", models.PositiveSmallIntegerField(default=0)),
                (
                    "cuenta",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="codigos_cambio",
                        to="usuarios.cuentausuario",
                    ),
                ),
            ],
        ),
    ]

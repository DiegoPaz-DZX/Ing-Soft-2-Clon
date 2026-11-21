from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cuentausuario",
            name="rol",
            field=models.CharField(
                choices=[("USUARIO", "Usuario"), ("ADMINISTRADOR", "Administrador")],
                default="USUARIO",
                max_length=15,
            ),
        ),
    ]

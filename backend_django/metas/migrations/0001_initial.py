from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("usuarios", "0002_cuentausuario_rol")]

    operations = [
        migrations.CreateModel(
            name="MetaAhorro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("objetivo_pen", models.DecimalField(decimal_places=2, max_digits=12)),
                ("total_abonado_pen", models.DecimalField(decimal_places=2, default=0, max_digits=12)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                ("actualizada_en", models.DateTimeField(auto_now=True)),
                (
                    "usuario",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="metas",
                        to="usuarios.cuentausuario",
                    ),
                ),
            ],
            options={"ordering": ["-actualizada_en", "-id"]},
        ),
    ]

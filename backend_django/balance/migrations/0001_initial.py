from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Movimiento",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tipo",
                    models.CharField(
                        choices=[("INGRESO", "Ingreso"), ("GASTO", "Gasto")],
                        max_length=7,
                    ),
                ),
                ("monto", models.DecimalField(decimal_places=2, max_digits=12)),
                ("fecha", models.DateField()),
                ("descripcion", models.CharField(max_length=200)),
            ],
        ),
    ]

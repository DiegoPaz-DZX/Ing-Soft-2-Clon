from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TokenRevocado",
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
                ("huella", models.CharField(max_length=64, unique=True)),
                ("expira_en", models.DateTimeField()),
                ("revocado_en", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "indexes": [
                    models.Index(fields=["expira_en"], name="sesion_toke_expira__idx")
                ]
            },
        ),
    ]

from django.db import migrations

import seguridad.CampoTextoCifrado


def cifrar_descripciones_existentes(apps, schema_editor):
    Movimiento = apps.get_model("balance", "Movimiento")
    for movimiento in Movimiento.objects.all().iterator():
        movimiento.descripcion = movimiento.descripcion
        movimiento.save(update_fields=["descripcion"])


class Migration(migrations.Migration):
    dependencies = [
        ("balance", "0004_merge_moneda_categoria"),
    ]

    operations = [
        migrations.AlterField(
            model_name="movimiento",
            name="descripcion",
            field=seguridad.CampoTextoCifrado.CampoTextoCifrado(max_length=200),
        ),
        migrations.RunPython(cifrar_descripciones_existentes, migrations.RunPython.noop),
    ]

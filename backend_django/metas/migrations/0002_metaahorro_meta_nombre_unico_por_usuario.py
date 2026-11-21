import django.db.models.functions.text
from django.db import migrations, models


def renombrar_metas_repetidas(apps, schema_editor):
    MetaAhorro = apps.get_model("metas", "MetaAhorro")
    usadas = set()

    for meta in MetaAhorro.objects.order_by("usuario_id", "id"):
        clave = (meta.usuario_id, meta.nombre.casefold())
        if clave not in usadas:
            usadas.add(clave)
            continue

        base = meta.nombre
        numero = 2
        while True:
            sufijo = f" ({numero})"
            nombre = f"{base[:120 - len(sufijo)]}{sufijo}"
            nueva_clave = (meta.usuario_id, nombre.casefold())
            if nueva_clave not in usadas:
                meta.nombre = nombre
                meta.save(update_fields=["nombre"])
                usadas.add(nueva_clave)
                break
            numero += 1


def no_revertir_renombrado(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('metas', '0001_initial'),
        ('usuarios', '0003_codigocambioclave'),
    ]

    operations = [
        migrations.RunPython(renombrar_metas_repetidas, no_revertir_renombrado),
        migrations.AddConstraint(
            model_name='metaahorro',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('nombre'), models.F('usuario'), name='meta_nombre_unico_por_usuario'),
        ),
    ]

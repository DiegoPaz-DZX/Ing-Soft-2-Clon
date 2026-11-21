import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0008_seguridad_postgresql'),
        ('metas', '0002_metaahorro_meta_nombre_unico_por_usuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='movimiento',
            name='meta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='movimientos_ahorro', to='metas.metaahorro'),
        ),
    ]

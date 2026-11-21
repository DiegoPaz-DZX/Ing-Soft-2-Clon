from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sesion', '0001_tokenrevocado'),
    ]

    operations = [
        migrations.RenameIndex(
            model_name='tokenrevocado',
            new_name='sesion_toke_expira__49d73f_idx',
            old_name='sesion_toke_expira__idx',
        ),
    ]

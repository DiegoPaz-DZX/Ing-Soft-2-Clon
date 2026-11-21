import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PreferenciaMoneda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('divisa', models.CharField(choices=[('PEN', 'Soles'), ('USD', 'Dólares')], default='PEN', max_length=3)),
                ('cuenta', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='preferencia_moneda', to='usuarios.cuentausuario')),
            ],
        ),
    ]

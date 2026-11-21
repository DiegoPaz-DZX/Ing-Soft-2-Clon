from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('preferencias', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoCambioDiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(unique=True)),
                ('soles_por_dolar', models.DecimalField(decimal_places=4, max_digits=10)),
                ('fuente', models.CharField(max_length=60)),
            ],
        ),
    ]

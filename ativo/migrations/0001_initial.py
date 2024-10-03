# Generated by Django 5.1.1 on 2024-10-03 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Ativo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_compra', models.DateField()),
                ('quantidade', models.DecimalField(decimal_places=10, default=0, max_digits=20)),
                ('valor_compra', models.DecimalField(decimal_places=2, max_digits=12)),
            ],
        ),
    ]

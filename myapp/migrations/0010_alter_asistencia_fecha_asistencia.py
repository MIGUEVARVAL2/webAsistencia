# Generated by Django 5.0.3 on 2024-03-11 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0009_asistencia_asistencia_estudiante'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asistencia',
            name='fecha_asistencia',
            field=models.DateField(),
        ),
    ]
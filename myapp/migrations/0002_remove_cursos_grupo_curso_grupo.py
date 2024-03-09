# Generated by Django 5.0.3 on 2024-03-08 18:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cursos',
            name='grupo_curso',
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id_grupo', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_grupo', models.CharField(max_length=100)),
                ('curso_grupo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='myapp.cursos')),
            ],
        ),
    ]
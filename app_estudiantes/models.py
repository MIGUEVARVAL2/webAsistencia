from django.db import models

class Estudiantes(models.Model):
    documento_estudiante = models.CharField(max_length=20, null=False)
    nombres_estudiante = models.CharField(max_length=100, null=False)
    apellidos_estudiante = models.CharField(max_length=100, null=False)
    correo_estudiante = models.EmailField(null=False)
    contrasenia_estudiante = models.CharField(max_length=100, null=False)
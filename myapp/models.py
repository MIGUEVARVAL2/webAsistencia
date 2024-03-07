from django.db import models

# Create your models here.

class Profesores(models.Model):
    documento_profesor = models.CharField(max_length=20, null=False)
    nombres_profesor = models.CharField(max_length=100, null=False)
    apellidos_profesor = models.CharField(max_length=100, null=False)
    correo_profesor = models.EmailField(null=False)
    contrasenia_profesor = models.CharField(max_length=100, null=False)

class Estudiantes(models.Model):
    documento_estudiante = models.CharField(max_length=20, null=False)
    nombres_estudiante = models.CharField(max_length=100, null=False)
    apellidos_estudiante = models.CharField(max_length=100, null=False)
    correo_estudiante = models.EmailField(null=False)
    contrasenia_estudiante = models.CharField(max_length=100, null=False)

class Cursos(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre_curso = models.CharField(max_length=100, null=False)
    grupo_curso = models.CharField(max_length=50, null=False)
    anio_curso = models.IntegerField(null=False)
    fecha_creacion_curso = models.DateTimeField(auto_now_add=True)
    profesor_curso = models.ForeignKey(Profesores, on_delete=models.CASCADE)

class EstudiantesCursos(models.Model):
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    curso = models.ForeignKey(Cursos, on_delete=models.CASCADE)


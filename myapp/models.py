from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Profesores(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    documento_profesor = models.CharField(max_length=20, null=False)
    nombres_profesor = models.CharField(max_length=100, null=False)
    apellidos_profesor = models.CharField(max_length=100, null=False)
    
class PlanesEstudio(models.Model):
    id_plan = models.CharField(max_length=10,primary_key=True)
    nombre_plan = models.CharField(max_length=100, null=False)

class Estudiantes(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    documento_estudiante = models.CharField(max_length=20, null=False)
    nombres_estudiante = models.CharField(max_length=100, null=False)
    apellidos_estudiante = models.CharField(max_length=100, null=False)
    plan_estudio = models.ForeignKey(PlanesEstudio, on_delete=models.CASCADE, null=True)


class Cursos(models.Model):
    id_curso = models.AutoField(primary_key=True)
    nombre_curso = models.CharField(max_length=100, null=False)
    anio_curso = models.IntegerField(null=False)
    semestre_curso = models.CharField(max_length=2, null=False, choices=[('1S', '1S'), ('2S', '2S')])
    fecha_creacion_curso = models.DateTimeField(auto_now_add=True)
    profesor_curso = models.ForeignKey(Profesores, on_delete=models.CASCADE)

class Grupos(models.Model):
    id_grupo = models.AutoField(primary_key=True)
    nombre_grupo = models.CharField(max_length=100, null=False)
    curso_grupo = models.ForeignKey(Cursos, on_delete=models.CASCADE)
    estudiantes_grupo = models.ManyToManyField(Estudiantes, through='Inscripcion')

class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupos, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.BooleanField(default=True)

class Asistencia(models.Model):
    id_asistencia = models.AutoField(primary_key=True)
    fecha_asistencia = models.DateField(null=False)
    activa = models.BooleanField(default=False)
    grupo = models.ForeignKey(Grupos, on_delete=models.CASCADE)

class Asistencia_estudiante(models.Model):
    id_asistencia_estudiante= models.AutoField(primary_key=True)
    registro_Asistencia = models.BooleanField(default=False)
    excusa= models.BooleanField(default=False, null=True)
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE)
    asistencia = models.ForeignKey(Asistencia, on_delete=models.CASCADE)

class Excusa_falta_estudiante(models.Model): 
    id_excusa = models.AutoField(primary_key=True) 
    motivo = models.CharField(max_length=100, null=False) 
    fecha_creacion_excusa = models.DateTimeField(auto_now_add=True)
    soporte_excusa = models.FileField(upload_to='soportes_excusas/',null=True, blank=True)
    excusa_valida= models.BooleanField(default=False)
    estudiante = models.ForeignKey(Estudiantes, on_delete=models.CASCADE) 
    asistencia_estudiante = models.ForeignKey(Asistencia_estudiante, on_delete=models.CASCADE)
    



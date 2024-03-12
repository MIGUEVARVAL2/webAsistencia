from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index,name="index"),
    path('cursos_estudiantes/', views.cursos_estudiantes,name="cursos_estudiantes"),
    path('informacion_curso/<int:grupo>/', views.informacion_curso,name="informacion_curso"),
    path('listar_estudiantes_curso/<int:grupo>/', views.listar_estudiantes_curso,name="listar_estudiantes_curso"),
    path('tomar_asistencia/<int:asistencia>', views.tomar_asistencia,name="tomar_asistencia"),
    path('perfil_profesor/', views.perfil_profesor,name="perfil_profesor"),

    path('listar_grupos_estudiantes/', views.listar_grupos_estudiantes, name='listar_grupos_estudiantes'),
    path('registrar_asistencia/<int:grupo>/', views.registrar_asistencia, name='registrar_asistencia'),

    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
]

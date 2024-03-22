from django.contrib import admin
from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index,name="index"),

    #Vistas para profesores
    path('cursos_estudiantes/', views.cursos_estudiantes,name="cursos_estudiantes"),
    path('informacion_curso/<int:grupo>/', views.informacion_curso,name="informacion_curso"),
    path('listar_estudiantes_curso/<int:grupo>/', views.listar_estudiantes_curso,name="listar_estudiantes_curso"),
    path('tomar_asistencia/<int:asistencia>', views.tomar_asistencia,name="tomar_asistencia"),
    path('perfil_profesor/', views.perfil_profesor,name="perfil_profesor"),
    path('informacion_estudiante/<int:id_estudiante>', views.informacion_estudiante,name="informacion_estudiante"),

    #Vistas para estudiantes
    path('listar_grupos_estudiantes/', views.listar_grupos_estudiantes, name='listar_grupos_estudiantes'),
    path('registrar_asistencia/<int:grupo>/', views.registrar_asistencia, name='registrar_asistencia'),
    path('perfil_estudiante/', views.perfil_estudiante, name='perfil_estudiante'),

    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),

    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

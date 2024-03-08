from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import Profesores, Cursos, Estudiantes, EstudiantesCursos
import plotly.graph_objects as go
import plotly.offline as opy


# Create your views here.
def index(request):
    if request.method == 'POST':
        rol = request.POST.get('rol')
        documento = request.POST.get('documento')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        correo = request.POST.get('correo')
        contrasenia = request.POST.get('contrasenia')
        if rol == 'profesor':
            Profesores.objects.create(
                documento_profesor = documento,
                nombres_profesor = nombres,
                apellidos_profesor = apellidos,
                correo_profesor = correo,
                contrasenia_profesor = contrasenia
            )

        elif rol == 'estudiante':
            Estudiantes.objects.create(
                documento_estudiante = documento,
                nombres_estudiante = nombres,
                apellidos_estudiante = apellidos,
                correo_estudiante = correo,
                contrasenia_estudiante = contrasenia
            )

    return render(request, 'index.html')

def cursos_estudiantes(request):
    return render(request, 'cursos_estudiantes.html')

def informacion_curso(request):
    return render(request, 'informacion_curso.html')

def listar_estudiantes_curso(request):
    return render(request, 'listar_estudiantes_curso.html')

def tomar_asistencia(request):
    return render(request, 'tomar_asistencia.html')

def perfil_profesor(request):
    # Crear gráfico

    fig = go.Figure(data=go.Bar(y=[0.98, 0.7, 0.8,0.9], x=['Curso A', 'Curso B', 'Curso C','Curso D']))
    colores=['#9ddea6']*len(fig.data[0].x)
    for i in range(0,len(colores),2):
        colores[i]='#67b072'
    fig.update_traces(marker_color=colores)
    fig.update_layout(
        title="Porcentaje de Asistencia para el semestre 2024-1",
        xaxis_title="Curso",
        yaxis_title="Porcentaje",
        yaxis_tickformat="%",
        yaxis=dict(tickformat=".0%")
    )   
    # Convertir a HTML
    graph = opy.plot(fig, auto_open=False, output_type='div')
    return render(request, 'perfil_profesor.html', {'graph': graph})
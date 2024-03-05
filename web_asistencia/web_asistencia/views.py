from django.http import HttpResponse
from django.shortcuts import render
from django.template import Template, Context
import plotly.graph_objects as go
import plotly.offline as opy


def index(request):
    return render(request, "index.html",{})

def informacion_curso(request):
    # Crear gráfico
    fig = go.Figure(data=go.Bar(y=[2, 3, 1]))
    # Convertir a HTML
    graph = opy.plot(fig, auto_open=False, output_type='div')

    return render(request, 'my_template.html', {'graph': graph})

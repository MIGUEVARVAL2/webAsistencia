import plotly.graph_objects as go
import plotly.offline as opy
import pandas as pd


# Supongamos que tienes los siguientes datos
data = {'Elemento': ['04/03', '05/03', '06/03', '07/03', '08/03'],
        'Frecuencia': [90, 80, 92, 93, 70]}

df = pd.DataFrame(data)

# Agregar títulos
fig = go.Figure(data=go.Bar(x=df['Elemento'], y=df['Frecuencia']))
fig.update_layout(title='Histórico de Asistencia', xaxis_title='Día Asistencia', yaxis_title='Asistencia')

# Guardar gráfico en un archivo HTML
opy.plot(fig, filename='tabla_frecuencias.html', auto_open=False)

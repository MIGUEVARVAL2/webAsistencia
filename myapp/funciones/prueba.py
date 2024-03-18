import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd

app = dash.Dash(__name__)

# Supongamos que tienes un DataFrame de pandas llamado df con las columnas 'curso', 'grupo', 'año' y 'semestre'
df = pd.read_csv('myapp/funciones/prueba.csv')
app.layout = html.Div([
    dcc.Dropdown(
        id='curso-dropdown',
        options=[{'label': i, 'value': i} for i in df['curso'].unique()],
        value=df['curso'].unique()[0]
    ),
    dcc.Dropdown(
        id='grupo-dropdown',
        options=[{'label': i, 'value': i} for i in df['grupo'].unique()],
        value=df['grupo'].unique()[0]
    ),
    dcc.Input(
        id='año-input',
        type='number',
        value=df['año'].min()
    ),
    dcc.Dropdown(
        id='semestre-dropdown',
        options=[{'label': i, 'value': i} for i in df['semestre'].unique()],
        value=df['semestre'].unique()[0]
    ),
    dcc.Graph(id='graph')
])

@app.callback(
    Output('graph', 'figure'),
    [Input('curso-dropdown', 'value'),
     Input('grupo-dropdown', 'value'),
     Input('año-input', 'value'),
     Input('semestre-dropdown', 'value')]
)
def update_graph(curso, grupo, año, semestre):
    filtered_df = df[(df['curso'] == curso) & (df['grupo'] == grupo) & (df['año'] == año) & (df['semestre'] == semestre)]
    return {
        'data': [{
            'x': filtered_df.index,
            'y': filtered_df['cantidad_asistencia'],
            'type': 'bar'
        }]
    }

if __name__ == '__main__':
    app.run_server(debug=True)
import pandas as pd

df = pd.read_excel('M:/Convocatoria/WebAplicacion/myapp/funciones/report (24).xls')
nombres_apellidos = df['APELLIDOS Y NOMBRE'].str.split(',', expand=True)
df['NOMBRES'] = nombres_apellidos[1].str.title()
df['APELLIDOS'] = nombres_apellidos[0].str.title()
plan= df['PLAN'].str.split(' - ', expand=True)
df['CODIGO_PLAN'] = plan[0]
df['NOMBRE_PLAN'] = plan[1]
df.drop('PLAN', axis=1, inplace=True)
df.drop('APELLIDOS Y NOMBRE', axis=1, inplace=True)
df.drop('OBSERVACIÓN', axis=1, inplace=True)
print(df)
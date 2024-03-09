import pandas as pd
# Assuming the file is stored in the variable 'file'
class ModificarListado:
    def __init__(self, datos_archivo):
        self.datos_archivo = pd.read_excel(datos_archivo)

    def modificar_datos_lista(self):
        df = self.datos_archivo.copy()
        nombres_apellidos = df['APELLIDOS Y NOMBRE'].str.split(',', expand=True)
        df['NOMBRES'] = nombres_apellidos[1].str.title()
        df['APELLIDOS'] = nombres_apellidos[0].str.title()
        df.drop('APELLIDOS Y NOMBRE', axis=1, inplace=True)
        return df

    def ejecutar(self):
        data = self.modificar_datos_lista()
        print(data)
    

ml= ModificarListado('M:/Convocatoria/WebAplicacion/myapp/funciones/report (24).xls')
ml.ejecutar()
import pandas as pd
from ..models import Estudiantes,Grupos, PlanesEstudio, Inscripcion
from django.contrib.auth.models import User

# Assuming the file is stored in the variable 'file'
class Crear_grupo_estudiantes:
    def __init__(self, datos_archivo,id_grupo):
        #Inicializa con los datos del archivo y el id del grupo
        self.__datos_archivo = pd.read_excel(datos_archivo)
        self.__id_grupo= id_grupo

    def modificar_datos_lista(self):
        #Lee el archivo de excel el cual es un formato exacto del SIA, separa los nombres y los apellido, separa el plan de estudio y elimina las columnas que no se necesitan
        df = self.__datos_archivo.copy()
        nombres_apellidos = df['APELLIDOS Y NOMBRE'].str.split(',', expand=True)
        df['NOMBRES'] = nombres_apellidos[1].str.title()
        df['APELLIDOS'] = nombres_apellidos[0].str.title()
        plan= df['PLAN'].str.split(' - ', expand=True)
        df['CODIGO_PLAN'] = plan[0]
        df['NOMBRE_PLAN'] = plan[1]
        df.drop('PLAN', axis=1, inplace=True)
        df.drop('APELLIDOS Y NOMBRE', axis=1, inplace=True)
        df.drop('OBSERVACIÓN', axis=1, inplace=True)
        #Elimina filas con espacios nulos
        df.dropna(inplace=True)
        #Retorna el dataframe con los datos organizados para la creación del estudiante y el usuario
        return df
    
    def cargar_estudiantes(self,datos):
        #Obtiene la lista de estudiantes del grupo, verifica si el estudiante es nuevo y revisa si tenía estado inactivo y lo cambia a activo y en caso de no tener registro, se crea el estudiante y se inscribe en el grupo
        grupo = Grupos.objects.get(id_grupo=self.__id_grupo)
        #Ciclo para recorrer los datos del archivo
        for _, row in datos.iterrows():
            #Consulta si el plan de estudio ya está registrado
            cod_plan = row['CODIGO_PLAN']
            plan_estudio = PlanesEstudio.objects.filter(id_plan=cod_plan).first()
            #En caso de no estar registrado se crea el plan de estudio
            if not plan_estudio:
                plan_estudio = PlanesEstudio.objects.create(id_plan=cod_plan, nombre_plan=row['NOMBRE_PLAN'])
            #Se valida si el usuario ya está registrado
            user = User.objects.filter(username=row['CORREO']).first()
            #En caso de no estar registrado se crea el usuario
            if not user:
                user = User.objects.create_user(username=row['CORREO'], email=row['CORREO'], password=str(row['DOCUMENTO']))
            #Se valida si el estudiante ya está registrado
            estudiante= Estudiantes.objects.filter(user=user).first()
            #En caso de no estar registrado se crea el estudiante
            if not estudiante:
                Estudiantes.objects.create(
                    user=user,
                    documento_estudiante=row['DOCUMENTO'],
                    nombres_estudiante=row['NOMBRES'],
                    apellidos_estudiante=row['APELLIDOS'],
                    plan_estudio=plan_estudio
                )
            #Se crea la inscripción para el estudiante en el grupo
            Inscripcion.objects.create(
                estudiante=Estudiantes.objects.get(user=user),
                grupo=grupo
            )
            


    def ejecutar(self):
        data = self.modificar_datos_lista()
        self.cargar_estudiantes(data)
    

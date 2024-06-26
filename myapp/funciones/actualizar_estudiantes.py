import pandas as pd
from ..models import Estudiantes,Grupos, PlanesEstudio, Inscripcion
from django.contrib.auth.models import User

# Función para actualizar el listado de estudiantes, verificar nuevos y eliminados
class actualizar_grupo_estudiantes:

    #Inicializa con los datos del archivo y el id del grupo
    def __init__(self, datos_archivo,id_grupo):
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
        df.dropna(inplace=True)
        return df
    
    def validar_estudiantes_eliminados(self,datos):
        #Obtiene la lista de estudiantes del grupo y verifica si el documento del estudiante no está en el archivo, en caso de que no esté se cambia el estado de la inscripción a False lo que significa que está inactivo
        lista_estudiantes= Estudiantes.objects.filter(grupos=self.__id_grupo)
        #Contador para usuarios eliminados
        cant_eliminados=0
        #Ciclo para recorrer los estudiantes del grupo
        for estudiante in lista_estudiantes:
            #Esta función se encarga de verificar si el documento del estudiante no está en el archivo
            documento = estudiante.documento_estudiante
            #En caso que no esté en el listado del SIA se cambia el estado de la inscripción a False
            if str(documento) not in str(datos['DOCUMENTO'].values):
                validar_inscripcion= Inscripcion.objects.filter(estudiante=estudiante,grupo=self.id_grupo).first()
                if validar_inscripcion:
                    validar_inscripcion.estado=False
                    validar_inscripcion.save()       
                    cant_eliminados+=1 
        #Retorna la cantidad de estudiantes eliminados
        return cant_eliminados

    def cargar_estudiantes(self,datos):
        #Obtiene la lista de estudiantes del grupo, verifica si el estudiante es nuevo y revisa si tenía estado inactivo y lo cambia a activo y en caso de no tener registro, se crea el estudiante y se inscribe en el grupo
        grupo = Grupos.objects.get(id_grupo=self.__id_grupo)
        #Contador para usuarios nuevos
        cant_nuevos=0
        #Ciclo para recorrer los datos del archivo
        for _, row in datos.iterrows():
            #Consulta si el estudiante tiene inscripción en el grupo
            validar_inscripcion= Inscripcion.objects.filter(estudiante__documento_estudiante=row['DOCUMENTO'],grupo=grupo).first()
            #En caso que no haya inscripción se crea el estudiante y se inscribe en el grupo
            if not validar_inscripcion:
                cod_plan = row['CODIGO_PLAN']
                plan_estudio = PlanesEstudio.objects.filter(id_plan=cod_plan).first()
                #Validar si el plan de estudio existe
                if not plan_estudio:
                    plan_estudio = PlanesEstudio.objects.create(id_plan=cod_plan, nombre_plan=row['NOMBRE_PLAN'])
                user = User.objects.filter(username=row['CORREO']).first()
                #Validar si el usuario existe
                if not user:
                    user = User.objects.create_user(username=row['CORREO'], email=row['CORREO'], password=str(row['DOCUMENTO']))
                estudiante= Estudiantes.objects.filter(user=user).first()
                #Validar si el estudiante existe
                if not estudiante:
                    #Crear el estudiante
                    Estudiantes.objects.create(
                        user=user,
                        documento_estudiante=row['DOCUMENTO'],
                        nombres_estudiante=row['NOMBRES'],
                        apellidos_estudiante=row['APELLIDOS'],
                        plan_estudio=plan_estudio
                    )
                #Crear la inscripción
                Inscripcion.objects.create(
                    estudiante=Estudiantes.objects.get(user=user),
                    grupo=grupo
                )
                #Contador de estudiantes nuevos
                cant_nuevos+=1
            #En caso de que el estudiante tenga inscripción y esté inactivo se cambia a activo activo
            elif validar_inscripcion.estado == False:
                validar_inscripcion.estado=True
                validar_inscripcion.save()
                cant_nuevos+=1
        #Retorna la cantidad de estudiantes nuevos
        return cant_nuevos

    def ejecutar(self):
        data = self.modificar_datos_lista()
        cant_eliminados=self.validar_estudiantes_eliminados(data)
        cant_nuevos=self.cargar_estudiantes(data)
        return cant_nuevos,cant_eliminados
    

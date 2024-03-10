import pandas as pd
from ..models import Estudiantes,Grupos, PlanesEstudio, Inscripcion
from django.contrib.auth.models import User

# Assuming the file is stored in the variable 'file'
class actualizar_grupo_estudiantes:
    def __init__(self, datos_archivo,id_grupo):
        self.datos_archivo = pd.read_excel(datos_archivo)
        self.id_grupo= id_grupo

    def modificar_datos_lista(self):
        df = self.datos_archivo.copy()
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
        lista_estudiantes= Estudiantes.objects.filter(grupos=self.id_grupo)
        cant_eliminados=0
        for estudiante in lista_estudiantes:
            documento = estudiante.documento_estudiante
            if str(documento) not in str(datos['DOCUMENTO'].values):
                validar_inscripcion= Inscripcion.objects.filter(estudiante=estudiante,grupo=self.id_grupo).first()
                if validar_inscripcion:
                    validar_inscripcion.estado=False
                    validar_inscripcion.save()       
                    cant_eliminados+=1 
        return cant_eliminados

    def cargar_estudiantes(self,datos):
        grupo = Grupos.objects.get(id_grupo=self.id_grupo)
        cant_nuevos=0
        for index, row in datos.iterrows():
            validar_inscripcion= Inscripcion.objects.filter(estudiante__documento_estudiante=row['DOCUMENTO'],grupo=grupo).first()
            if not validar_inscripcion:
                cod_plan = row['CODIGO_PLAN']
                plan_estudio = PlanesEstudio.objects.filter(id_plan=cod_plan).first()
                if not plan_estudio:
                    plan_estudio = PlanesEstudio.objects.create(id_plan=cod_plan, nombre_plan=row['NOMBRE_PLAN'])
                user = User.objects.filter(username=row['CORREO']).first()
                if not user:
                    user = User.objects.create_user(username=row['CORREO'], email=row['CORREO'], password=str(row['DOCUMENTO']))
                estudiante= Estudiantes.objects.filter(user=user).first()
                if not estudiante:
                    Estudiantes.objects.create(
                        user=user,
                        documento_estudiante=row['DOCUMENTO'],
                        nombres_estudiante=row['NOMBRES'],
                        apellidos_estudiante=row['APELLIDOS'],
                        plan_estudio=plan_estudio
                    )
                Inscripcion.objects.create(
                    estudiante=Estudiantes.objects.get(user=user),
                    grupo=grupo
                )
                cant_nuevos+=1
                
        return cant_nuevos

    def ejecutar(self):
        data = self.modificar_datos_lista()
        cant_eliminados=self.validar_estudiantes_eliminados(data)
        cant_nuevos=self.cargar_estudiantes(data)
        return cant_nuevos,cant_eliminados
    

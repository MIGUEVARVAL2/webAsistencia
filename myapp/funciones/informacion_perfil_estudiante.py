from ..models import Estudiantes, Cursos, User, Grupos, Asistencia, Asistencia_estudiante

#Información para listar la información del estudiante en la vista del estudiante
class informacion_estudiante:
        
        def __init__(self, estudiante):
            #Obtiene el estudiante
            self.__estudiante = Estudiantes.objects.get(id=estudiante)

        @property
        def get_datos_estudiante(self):
            return self.__estudiante
        
        def editar_contrasenia(self, contrasenia):
            user= User.objects.get(id=self.__estudiante.user.id)
            user.password = contrasenia
            user.save()
            return True
        
        def listar_asistencia(self):
            #Obtiene los grupos del estudiante y las asistencias del grupo
            ultimo_periodo = Cursos.objects.latest('anio_curso', 'semestre_curso')
            ultimo_anio = ultimo_periodo.anio_curso
            #obtengo el último semestre
            ultimo_semestre = ultimo_periodo.semestre_curso
            grupos = Grupos.objects.filter(estudiantes_grupo=self.__estudiante, curso_grupo__anio_curso=ultimo_anio, curso_grupo__semestre_curso=ultimo_semestre)
            asistencias_estudiante = Asistencia_estudiante.objects.filter(estudiante=self.__estudiante, asistencia__grupo__curso_grupo__anio_curso=ultimo_anio, asistencia__grupo__curso_grupo__semestre_curso=ultimo_semestre)
            #Guardo los datos necesarios para listar la asistencia del estudiante
            data = []
            #Ciclo para recorrer los grupos
            for grupo in grupos:
                #Obtiene las asistencias del grupo
                asistencias_grupo = Asistencia.objects.filter(grupo=grupo)
                total_asistencias_grupo = asistencias_grupo.count()
                #Obtiene las asistencias que tienen registro (Asistió) del estudiante en el grupo
                asistencias_estudiante_grupo = asistencias_estudiante.filter(asistencia__in=asistencias_grupo, registro_Asistencia=True)
                total_asistencias_estudiante_grupo = asistencias_estudiante_grupo.count()
                #En caso de que no hayan asistencias el porcentaje es igual a 0
                if total_asistencias_grupo == 0:
                    porcentaje_asistencia_grupo = 0
                #En caso de que haya asistencias se calcula el porcentaje de asistencia
                else:
                    porcentaje_asistencia_grupo = round((total_asistencias_estudiante_grupo / total_asistencias_grupo) * 100,2)
                periodo=f'{ultimo_periodo.anio_curso}-{ultimo_periodo.semestre_curso}'
                data.append({
                    'codigo_curso': grupo.curso_grupo.id_curso,
                    'curso': grupo.curso_grupo.nombre_curso,
                    'grupo': grupo.nombre_grupo,
                    'asistencias_estudiante': total_asistencias_estudiante_grupo,
                    'total_asistencias_grupo': total_asistencias_grupo,
                    'porcentaje_asistencia_grupo': porcentaje_asistencia_grupo,
                })
            
            return data,periodo
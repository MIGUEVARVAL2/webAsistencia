from ..models import Estudiantes, Grupos, Asistencia, Asistencia_estudiante

#Información para listar la información del estudiante en la vista del profesor
class informacion_estudiante_profesor:
        
    def __init__(self, estudiante):
        #Obtiene el estudiante
        self.__estudiante = Estudiantes.objects.get(id=estudiante)

    @property
    def datos_estudiante(self):
        return self.__estudiante
        
    def listar_asistencia(self,profesor):
        #Obtiene los grupos del estudiante y las asistencias del grupo  
        grupos = Grupos.objects.filter(estudiantes_grupo=self.__estudiante,curso_grupo__profesor_curso=profesor).order_by('curso_grupo__anio_curso', 'curso_grupo__semestre_curso')
        #Obtiene las asistencias del estudiante para los grupos del profesor
        asistencias_estudiante = Asistencia_estudiante.objects.filter(estudiante=self.__estudiante,asistencia__grupo__curso_grupo__profesor_curso=profesor)
        #Guardamos todos los datos necesarios para listar la asistencia del estudiante
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
            data.append({
                'codigo_curso': grupo.curso_grupo.id_curso,
                'curso': grupo.curso_grupo.nombre_curso,
                'grupo': grupo.nombre_grupo,
                'asistencias_estudiante': total_asistencias_estudiante_grupo,
                'total_asistencias_grupo': total_asistencias_grupo,
                'porcentaje_asistencia_grupo': porcentaje_asistencia_grupo,
                'periodo': f'{grupo.curso_grupo.anio_curso}-{grupo.curso_grupo.semestre_curso}'
            })
            
        return data
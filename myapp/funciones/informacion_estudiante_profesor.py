from ..models import Estudiantes, Cursos, User, Grupos, Asistencia, Asistencia_estudiante, Profesores
import plotly.graph_objects as go
import plotly.offline as opy

class informacion_estudiante:
        
        def __init__(self, estudiante):
            self.estudiante = Estudiantes.objects.get(id=estudiante)

        def datos_estudiante(self):
            return self.estudiante
        
        def listar_asistencia(self,profesor):
            grupos = Grupos.objects.filter(estudiantes_grupo=self.estudiante,curso_grupo__profesor_curso=profesor).order_by('curso_grupo__anio_curso', 'curso_grupo__semestre_curso')
            asistencias_estudiante = Asistencia_estudiante.objects.filter(estudiante=self.estudiante)
            
            data = []
            for grupo in grupos:
                asistencias_grupo = Asistencia.objects.filter(grupo=grupo)
                total_asistencias_grupo = asistencias_grupo.count()
                asistencias_estudiante_grupo = asistencias_estudiante.filter(asistencia__in=asistencias_grupo, registro_Asistencia=True)
                total_asistencias_estudiante_grupo = asistencias_estudiante_grupo.count()
                if total_asistencias_grupo == 0:
                    porcentaje_asistencia_grupo = 0
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
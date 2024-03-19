from ..models import Estudiantes, Cursos, User, Grupos, Asistencia, Asistencia_estudiante
import plotly.graph_objects as go
import plotly.offline as opy

class informacion_estudiante:
        
        def __init__(self, estudiante):
            self.estudiante = Estudiantes.objects.get(id=estudiante)

        def datos_estudiante(self):
            return self.estudiante
        
        def editar_contrasenia(self, contrasenia):
            user= User.objects.get(id=self.estudiante.user.id)
            user.password = contrasenia
            user.save()
            return True
        
        def listar_asistencia(self):
            ultimo_periodo = Cursos.objects.latest('anio_curso', 'semestre_curso')
            ultimo_anio = ultimo_periodo.anio_curso
            ultimo_semestre = ultimo_periodo.semestre_curso
            grupos = Grupos.objects.filter(estudiantes_grupo=self.estudiante, curso_grupo__anio_curso=ultimo_anio, curso_grupo__semestre_curso=ultimo_semestre)
            asistencias_estudiante = Asistencia_estudiante.objects.filter(estudiante=self.estudiante, asistencia__grupo__curso_grupo__anio_curso=ultimo_anio, asistencia__grupo__curso_grupo__semestre_curso=ultimo_semestre)
            
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
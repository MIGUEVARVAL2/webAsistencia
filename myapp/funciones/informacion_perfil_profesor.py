from ..models import Profesores, Cursos, User, Grupos, Asistencia, Asistencia_estudiante
import plotly.graph_objects as go
import plotly.offline as opy

class informacion_profesor:
        
        def __init__(self, profesor):
            self.profesor = Profesores.objects.get(id=profesor)

        def datos_profesor(self):
            return self.profesor
        
        def editar_contrasenia(self, contrasenia):
            user= User.objects.get(id=self.profesor.user.id)
            user.password = contrasenia
            user.save()
            return True
        
        def semestres(self):
            semestre = Cursos.objects.filter(profesor_curso=self.profesor).values('anio_curso', 'semestre_curso').distinct().order_by('-anio_curso', '-semestre_curso')
            return semestre
        
        def listar_asistencia(self):
            cursos = Grupos.objects.filter(curso_grupo__profesor_curso=self.profesor).order_by('-curso_grupo__anio_curso', '-curso_grupo__semestre_curso', 'curso_grupo__nombre_curso', 'nombre_grupo')
            for curso in cursos:
                asistencias= Asistencia.objects.filter(grupo=curso)
                curso.cantidad_asistencia = asistencias.count()
                curso.porcentaje_asistencia_total = 0
                for asistencia in asistencias:
                    cantidad_registros = Asistencia_estudiante.objects.filter(asistencia=asistencia).count()
                    cantidad_registros_asistencia = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=True).count()
                    if cantidad_registros > 0:
                        porcentaje = cantidad_registros_asistencia / cantidad_registros
                    else:
                        porcentaje = 0
                    curso.porcentaje_asistencia_total += porcentaje
                if curso.cantidad_asistencia > 0:
                    curso.porcentaje_asistencia_total = round((curso.porcentaje_asistencia_total / curso.cantidad_asistencia)*100,2)    
            
            return cursos


        def porcentaje_asistencia_cursos(self,semestre=None):
            if semestre:
                ultimo_periodo=semestre.split('-')
                ultimo_anio = ultimo_periodo[0]
                ultimo_semestre = ultimo_periodo[1]
            else:
                ultimo_periodo = Cursos.objects.filter(profesor_curso=self.profesor).latest('anio_curso', 'semestre_curso')
                ultimo_anio = ultimo_periodo.anio_curso
                ultimo_semestre = ultimo_periodo.semestre_curso
            
            cursos = Cursos.objects.filter(profesor_curso=self.profesor,anio_curso=ultimo_anio,semestre_curso=ultimo_semestre).order_by('nombre_curso')
            valor_x = []
            valor_y = []
            valor_y_por_grupo = []
            nombre_grupo_por_curso=[]
            for curso in cursos:
                porcentajes_por_grupo = []
                nombre_grupo= []
                grupos = Grupos.objects.filter(curso_grupo=curso).order_by('nombre_grupo')
                curso.cantidad_asistencia_total = 0
                curso.porcentaje_asistencia_total = 0
                for grupo in grupos:
                    asistencias = Asistencia.objects.filter(grupo=grupo)
                    grupo.cantidad_asistencia = asistencias.count()
                    grupo.porcentaje_asistencia_total = 0
                    for asistencia in asistencias:
                        cantidad_registros = Asistencia_estudiante.objects.filter(asistencia=asistencia).count()
                        cantidad_registros_asistencia = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=True).count()
                        if cantidad_registros > 0:
                            porcentaje = cantidad_registros_asistencia / cantidad_registros
                        else:
                            porcentaje = 0
                        grupo.porcentaje_asistencia_total += porcentaje
                    if grupo.cantidad_asistencia > 0:
                        grupo.porcentaje_asistencia_total = round((grupo.porcentaje_asistencia_total / grupo.cantidad_asistencia), 2)
                    curso.cantidad_asistencia_total += grupo.cantidad_asistencia
                    curso.porcentaje_asistencia_total += grupo.porcentaje_asistencia_total
                    porcentajes_por_grupo.append(grupo.porcentaje_asistencia_total)
                    nombre_grupo.append(f'{curso.id_curso}-{grupo.nombre_grupo}')
                valor_y_por_grupo.append(porcentajes_por_grupo)
                nombre_grupo_por_curso.append(nombre_grupo)
                if curso.cantidad_asistencia_total > 0:
                    curso.porcentaje_asistencia_total = round((curso.porcentaje_asistencia_total / curso.cantidad_asistencia_total), 2)
                valor_x.append(curso.nombre_curso)
                valor_y.append(curso.porcentaje_asistencia_total)
            valor_x = [x[:20] + '...' if len(x) > 20 else x for x in valor_x]
            return valor_x, valor_y, valor_y_por_grupo, nombre_grupo_por_curso


        def graficar(self,valor_x,valor_y,valor_y_por_grupo,nombres):
            data = []
            for i in range(len(valor_y_por_grupo)):
                for j in range(len(valor_y_por_grupo[i])):
                    nombre_grupo = nombres[i][j]
                    data.append(go.Bar(name=str(nombre_grupo), x=[valor_x[i]], y=[valor_y_por_grupo[i][j]]))

            fig = go.Figure(data=data)
            colores=['#9ddea6']*len(fig.data[0].x)
            for i in range(0,len(colores),2):
                colores[i]='#67b072'
            fig.update_traces(marker_color=colores)
            fig.update_layout(
                barmode='stack',
                title="Porcentaje de Asistencia",
                xaxis_title="Curso",
                yaxis_title="Porcentaje",
                yaxis_tickformat="%",
                yaxis=dict(tickformat=".0%")
            )   
            # Convertir a HTML
            graph = opy.plot(fig, auto_open=False, output_type='div')
            return graph
        
        def crear_grafica_total(self,semestre=None):
            valor_x, valor_y, valor_y_por_grupo, nombres = self.porcentaje_asistencia_cursos(semestre)
            return self.graficar(valor_x,valor_y,valor_y_por_grupo,nombres)
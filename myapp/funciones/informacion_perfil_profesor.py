from ..models import Profesores, Cursos, User, Grupos, Asistencia, Asistencia_estudiante
import plotly.graph_objects as go
import plotly.offline as opy

class informacion_profesor:
        
        def __init__(self, profesor):
            #Obtiene el profesor
            self.__profesor = Profesores.objects.get(id=profesor)

        @property
        def get_datos_profesor(self):
            return self.__profesor
        
        def editar_contrasenia(self, contrasenia):
            #Edita la contraseña del profesor
            user= User.objects.get(id=self.__profesor.user.id)
            user.password = contrasenia
            user.save()
            return True
        
        def semestres(self):
            #Obtiene los años y semestres de los cursos del profesor
            semestre = Cursos.objects.filter(profesor_curso=self.__profesor).values('anio_curso', 'semestre_curso').distinct().order_by('-anio_curso', '-semestre_curso')
            return semestre
        
        def listar_asistencia(self):
            #Obtiene los grupos del profesor y las asistencias del grupo
            cursos = Grupos.objects.filter(curso_grupo__profesor_curso=self.__profesor).order_by('-curso_grupo__anio_curso', '-curso_grupo__semestre_curso', 'curso_grupo__nombre_curso', 'nombre_grupo')
            #Ciclo para recorrer los cursos y realizar los calculos correspondientes
            for curso in cursos:
                #Obtiene las asistencias del grupo
                asistencias= Asistencia.objects.filter(grupo=curso)
                #Guarda la cantidad de asistencias y el porcentaje de asistencia
                curso.cantidad_asistencia = asistencias.count()
                curso.porcentaje_asistencia_total = 0
                #Ciclo para recorrer las asistencias por grupo
                for asistencia in asistencias:
                    #Obtiene la cantidad de asistencias y la cantidad de asistencias con registros (Asistió)
                    cantidad_registros = Asistencia_estudiante.objects.filter(asistencia=asistencia).count()
                    cantidad_registros_asistencia = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=True).count()
                    #Va calculando el porcentaje de asistencia y lo suma al porcentaje total
                    if cantidad_registros > 0:
                        porcentaje = cantidad_registros_asistencia / cantidad_registros
                    else:
                        porcentaje = 0
                    curso.porcentaje_asistencia_total += porcentaje
                if curso.cantidad_asistencia > 0:
                    #Calcula el porcentaje de asistencia total redondeado a un decimal
                    curso.porcentaje_asistencia_total = round((curso.porcentaje_asistencia_total / curso.cantidad_asistencia)*100,1)    
            
            return cursos


        def porcentaje_asistencia_cursos(self,semestre=None):
            #En caso de que envíen el semestre, se obtienen los cursos de ese semestre
            if semestre:
                ultimo_periodo=semestre.split('-')
                ultimo_anio = ultimo_periodo[0]
                ultimo_semestre = ultimo_periodo[1]
            #En caso contrario se obtienen los cursos del último semestre
            else:
                ultimo_periodo = Cursos.objects.filter(profesor_curso=self.__profesor).latest('anio_curso', 'semestre_curso')
                ultimo_anio = ultimo_periodo.anio_curso
                ultimo_semestre = ultimo_periodo.semestre_curso
            #Obtiene los cursos del profesor y los ordena
            cursos = Cursos.objects.filter(profesor_curso=self.__profesor,anio_curso=ultimo_anio,semestre_curso=ultimo_semestre).order_by('nombre_curso')
    
            valor_x = []
            valor_y = []
            valor_y_por_grupo = []
            nombre_grupo_por_curso=[]
            #Ciclo para recorrer los cursos y realizar los calculos correspondientes
            for curso in cursos:
                #Lista que se va a guardar en y
                porcentajes_por_grupo = []
                #Lista que se va a guardar en x
                nombre_grupo= []
                #Obtiene los grupos del curso y los ordena
                grupos = Grupos.objects.filter(curso_grupo=curso).order_by('nombre_grupo')
                #Creo dos nuevos datos para la información del curso
                curso.cantidad_asistencia_total = 0
                curso.porcentaje_asistencia_total = 0
                #Ciclo para recorrer los grupos y realizar los calculos correspondientes
                for grupo in grupos:
                    #Obtiene las asistencias del grupo
                    asistencias = Asistencia.objects.filter(grupo=grupo)
                    #Creo dos nuevos datos para la información del grupo
                    grupo.cantidad_asistencia = asistencias.count()
                    grupo.porcentaje_asistencia_total = 0
                    #Ciclo para recorrer las asistencias por grupo
                    for asistencia in asistencias:
                        #Caulculo del porcentaje de asistencia por grupo
                        cantidad_registros = Asistencia_estudiante.objects.filter(asistencia=asistencia).count()
                        cantidad_registros_asistencia = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=True).count()
                        if cantidad_registros > 0:
                            porcentaje = cantidad_registros_asistencia / cantidad_registros
                        else:
                            porcentaje = 0
                        #Suma el porcentaje de asistencia al porcentaje total del grupo
                        grupo.porcentaje_asistencia_total += porcentaje
                    #Calcula el porcentaje de asistencia total redondeado a un decimal
                    if grupo.cantidad_asistencia > 0:
                        grupo.porcentaje_asistencia_total = round((grupo.porcentaje_asistencia_total / grupo.cantidad_asistencia), 1)
                    #Suma la cantidad de asistencias y el porcentaje de asistencia al curso
                    curso.cantidad_asistencia_total += grupo.cantidad_asistencia
                    curso.porcentaje_asistencia_total += grupo.porcentaje_asistencia_total
                    #Guarda los datos de asistencias en las listas
                    porcentajes_por_grupo.append(grupo.porcentaje_asistencia_total)
                    nombre_grupo.append(f'{curso.id_curso}-{grupo.nombre_grupo}')
                #Guarda los datos del curso
                valor_y_por_grupo.append(porcentajes_por_grupo)
                nombre_grupo_por_curso.append(nombre_grupo)
                #Calcula el porcentaje de asistencia total redondeado a un decimal
                if curso.cantidad_asistencia_total > 0:
                    curso.porcentaje_asistencia_total = round((curso.porcentaje_asistencia_total / curso.cantidad_asistencia_total), 1)
                valor_x.append(curso.nombre_curso)
                valor_y.append(curso.porcentaje_asistencia_total)
            #Recorto los valores de x para los casos en los que el nombre del curso sea muy largo (Para no afectar la gráfica)
            valor_x = [x[:20] + '...' if len(x) > 20 else x for x in valor_x]
            return valor_x, valor_y, valor_y_por_grupo, nombre_grupo_por_curso


        def graficar(self,valor_x,valor_y,valor_y_por_grupo,nombres):
            data = []
            #Ciclo para recorrer los datos y crear la gráfica usando como valores en x CodigoCurso-NombreGrupo
            for i in range(len(valor_y_por_grupo)):
                for j in range(len(valor_y_por_grupo[i])):
                    nombre_grupo = nombres[i][j]
                    data.append(go.Bar(name=str(nombre_grupo), x=[valor_x[i]], y=[valor_y_por_grupo[i][j]]))
            #Asigno las configuraciones del grafico y los colores
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
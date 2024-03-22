from ..models import Asistencia, Asistencia_estudiante
import plotly.graph_objects as go
import plotly.offline as opy

class informacion_listado_asistencia:

    def __init__(self, id_grupo):
        self.id_grupo = id_grupo

    def listar_asistencia(self):
        #Obtiene las asistencias del grupo y las lista de forma descendente
        asistencias = Asistencia.objects.filter(grupo=self.id_grupo).order_by('-fecha_asistencia')
        return asistencias
    
    def info_asistencia(self, asistencias):
        #Obtiene la información de la asistencia, la cantidad de inasistencias y el porcentaje de asistencia    
        # Guarda asistencia,cantidad_total_inasistencia,porcentaje_asistencia para listarlo en la pagina
        datos = []
        # Guarda el porcentaje de asistencia para graficar
        porcentajes = []
        # Guarda el valor de x para graficar que sería el ID asistencia y la fecha
        valor_x = []
        #Ciclo para recorrer las asistencias y hacer los calculos correspondientes
        for asistencia in asistencias:
            #Obtiene la cantidad de inasistencias y la cantidad total de estudiantes
            asistencia_estudiante = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=False)
            cantidad_total_inasistencia = asistencia_estudiante.count()
            asistencia_estudiante = Asistencia_estudiante.objects.filter(asistencia=asistencia)
            cantidad_total_estudiantes = asistencia_estudiante.count()
            #En casso de que no haya estudiantes se pone el porcentaje de asistencia en 100%
            if cantidad_total_estudiantes == 0:
                porcentaje_asistencia = 100
            #En caso de que haya estudiantes se calcula el porcentaje de asistencia
            else:
                #Calcula el porcentaje de asistencia redondeado a un decimal
                porcentaje_asistencia = round(((cantidad_total_estudiantes - cantidad_total_inasistencia) / cantidad_total_estudiantes) * 100,1)
            datos.append((asistencia,cantidad_total_inasistencia,porcentaje_asistencia))
            valor_x.append(f'{asistencia.id_asistencia}-{asistencia.fecha_asistencia.strftime("%d/%m/%Y")}')
            porcentajes.append(porcentaje_asistencia/100)

        #Grafica el porcentaje de asistencia
        fig = go.Figure(data=[go.Bar(x=valor_x, y=porcentajes, offsetgroup=0)])
        fig.update_layout(title='Porcentaje de Asistencia por Asistencia', xaxis_title='Asistencia', yaxis_title='Porcentaje de Asistencia')
        colores=['#9ddea6']*len(fig.data[0].x)
        for i in range(0,len(colores),2):
            colores[i]='#67b072'
        fig.update_traces(marker_color=colores)
        fig.update_layout(
            
            title="Porcentaje de Asistencia",
            xaxis_title="Asistencia",
            yaxis_title="Porcentaje",
            yaxis_tickformat="%",
            yaxis=dict(tickformat=".0%")
        )
        grafica = opy.plot(fig, auto_open=False, output_type='div')

        return datos,grafica
    


        
        
    
    def ejecutar(self):
        asistencia= self.listar_asistencia()
        datos,grafica= self.info_asistencia(asistencia)
        
        return datos,grafica
    
    def buscar_asistencia(self,fecha):
        #Busca la asistencia por fecha y la ordena de forma descendente
        asistencia= Asistencia.objects.filter(grupo=self.id_grupo,fecha_asistencia=fecha).order_by('-fecha_asistencia')
        datos,_= self.info_asistencia(asistencia)
        return datos


    
            
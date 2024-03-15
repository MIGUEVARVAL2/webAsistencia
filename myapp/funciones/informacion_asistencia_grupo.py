from ..models import Asistencia,Grupos, Asistencia_estudiante


class informacion_listado_asistencia:

    def __init__(self, id_grupo):
        self.id_grupo = id_grupo

    def listar_asistencia(self):
        asistencias = Asistencia.objects.filter(grupo=self.id_grupo).order_by('-fecha_asistencia')
        return asistencias
    
    def info_asistencia(self, asistencias):
        datos = []
        for asistencia in asistencias:
            asistencia_estudiante = Asistencia_estudiante.objects.filter(asistencia=asistencia, registro_Asistencia=False)
            cantidad_total_inasistencia = asistencia_estudiante.count()
            asistencia_estudiante = Asistencia_estudiante.objects.filter(asistencia=asistencia)
            cantidad_total_estudiantes = asistencia_estudiante.count()
            if cantidad_total_estudiantes == 0:
                porcentaje_asistencia = 100
            else:
                porcentaje_asistencia = round(((cantidad_total_estudiantes - cantidad_total_inasistencia) / cantidad_total_estudiantes) * 100,1)
            datos.append((asistencia,cantidad_total_inasistencia,porcentaje_asistencia))
        return datos
    
    def ejecutar(self):
        asistencia= self.listar_asistencia()
        datos= self.info_asistencia(asistencia)
        
        return datos
    
    def buscar_asistencia(self,fecha):
        asistencia= Asistencia.objects.filter(grupo=self.id_grupo,fecha_asistencia=fecha).order_by('-fecha_asistencia')
        datos= self.info_asistencia(asistencia)
        return datos


    
            
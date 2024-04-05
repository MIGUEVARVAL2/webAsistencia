from ..models import Asistencia,Estudiantes, Excusa_falta_estudiante


class informacion_listado_tomar_asistencia:

    def __init__(self,asistencia):
        #Obtiene la asistencia
        self.__asistencia = Asistencia.objects.get(id_asistencia=asistencia)

    def listar_asistencia(self):
        #Listo la información de la asistencia con los estudiantes activos que son los que registraron asistencia y los inactivos
        grupo = self.__asistencia.grupo
        estudiantes_activos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.__asistencia,
            asistencia_estudiante__registro_Asistencia=True
        )
        #Para los inactivos se obtiene la información de la excusa
        estudiantes_inactivos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.__asistencia,
            asistencia_estudiante__registro_Asistencia=False
        ).values('id', 'documento_estudiante', 'nombres_estudiante', 'apellidos_estudiante', 'plan_estudio', 'user__email', 'asistencia_estudiante__excusa')
        fecha= self.__asistencia.fecha_asistencia
        estado_asistencia= self.__asistencia.activa
        #obtenfo las excusas de los estudiantes
        excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=self.__asistencia)
        return grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta
    
    def buscar_estudiante_ausente(self,documento):
        #Busco los estudiantes ausentes
        grupo = self.__asistencia.grupo
        estudiantes_activos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.__asistencia,
            asistencia_estudiante__registro_Asistencia=True
        )
        estudiantes_inactivos = Estudiantes.objects.filter(
            documento_estudiante__startswith=documento,
            asistencia_estudiante__asistencia=self.asistencia,
            asistencia_estudiante__registro_Asistencia=False
        ).values('id', 'documento_estudiante', 'nombres_estudiante', 'apellidos_estudiante', 'plan_estudio', 'user__email', 'asistencia_estudiante__excusa')
        fecha= self.__asistencia.fecha_asistencia
        estado_asistencia= self.__asistencia.activa
        excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=self.asistencia)
        return grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta
    
    def buscar_estudiante_presente(self,documento):
        #Busco los estudiantes presentes
        grupo = self.__asistencia.grupo
        estudiantes_activos = Estudiantes.objects.filter(
            documento_estudiante__startswith=documento,
            asistencia_estudiante__asistencia=self.__asistencia,
            asistencia_estudiante__registro_Asistencia=True
        )
        estudiantes_inactivos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.__asistencia,
            asistencia_estudiante__registro_Asistencia=False
        ).values('id', 'documento_estudiante', 'nombres_estudiante', 'apellidos_estudiante', 'plan_estudio', 'user__email', 'asistencia_estudiante__excusa')
        fecha= self.__asistencia.fecha_asistencia
        estado_asistencia= self.__asistencia.activa
        excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=self.__asistencia)
        return grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta
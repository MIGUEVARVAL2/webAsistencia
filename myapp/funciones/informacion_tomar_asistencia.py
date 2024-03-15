from ..models import Asistencia,Estudiantes, Excusa_falta_estudiante


class informacion_listado_tomar_asistencia:

    def __init__(self,asistencia):
        self.asistencia = Asistencia.objects.get(id_asistencia=asistencia)

    def listar_asistencia(self):
        grupo = self.asistencia.grupo
        estudiantes_activos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.asistencia,
            asistencia_estudiante__registro_Asistencia=True
        )
        estudiantes_inactivos = Estudiantes.objects.filter(
            asistencia_estudiante__asistencia=self.asistencia,
            asistencia_estudiante__registro_Asistencia=False
        ).values('id', 'documento_estudiante', 'nombres_estudiante', 'apellidos_estudiante', 'plan_estudio', 'user__email', 'asistencia_estudiante__excusa')
        fecha= self.asistencia.fecha_asistencia
        estado_asistencia= self.asistencia.activa
        excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=self.asistencia)
        return grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta
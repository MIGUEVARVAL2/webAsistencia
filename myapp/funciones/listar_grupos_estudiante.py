from ..models import Cursos,Grupos, Inscripcion


class informacion_listado_cursos:

    def __init__(self, id_estudiante):
        self.id_estudiante = id_estudiante

    def listar_cursos(self):
        #listo los cursos del estudiante y los ordeno
        grupos = Grupos.objects.filter(estudiantes_grupo=self.id_estudiante).order_by('-id_grupo')
        return grupos
    
    def ejecutar(self):
        cursos= self.listar_cursos()
        
        return cursos


    
            
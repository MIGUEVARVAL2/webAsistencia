from ..models import Cursos,Grupos


class informacion_listado_cursos:

    def __init__(self, id_profesor):
        self.id_profesor = id_profesor

    def listar_cursos(self):
        cursos = Cursos.objects.filter(profesor_curso=self.id_profesor)
        return cursos
    
    def cantidad_estudiantes(self, grupo):
        estudiantes = EstudiantesCursos.objects.filter(grupo=grupo)
        cantidad = estudiantes.count()
        return cantidad

    def listar_grupos(self, cursos):
        datos = []
        for curso in cursos:
            grupos_curso = Grupos.objects.filter(curso_grupo=curso)
            datos.append(curso,grupos_curso)
        return datos
    
    
    
    def ejecutar(self):
        cursos= self.listar_cursos()
        datos= self.listar_grupos(cursos)
        
        return datos


    
            
from ..models import Cursos,Grupos, Inscripcion


class informacion_listado_cursos:

    def __init__(self, id_profesor):
        self.__id_profesor = id_profesor

    def listar_cursos(self):
        #listo los cursos del profesor y los ordeno 
        cursos = Cursos.objects.filter(profesor_curso=self.__id_profesor).order_by('-anio_curso', '-semestre_curso', '-id_curso')
        return cursos
    
    def cantidad_estudiantes(self, grupo):
        #Obtengo la cantidad de estudiantes en un grupo
        estudiantes = Inscripcion.objects.filter(grupo=grupo)
        cantidad = estudiantes.count()
        return cantidad

    def listar_grupos(self, cursos):
        #Obtengo los grupos de cada curso y la cantidad de estudiantes en cada grupo
        #Guardo curso,grupos_curso,cantidad_total_estudiantes,cantidad_grupos
        datos = []
        #Ciclo para recorrer los cursos
        for curso in cursos:
            #Obtengo los grupos del curso y los ordeno
            grupos_curso = Grupos.objects.filter(curso_grupo=curso).order_by('id_grupo')
            #Inicializo la cantidad total de estudiantes
            cantidad_total_estudiantes = 0
            #Ciclo para recorrer los grupos del curso
            for grupo in grupos_curso:
                #Obtengo la cantidad de estudiantes en un grupo
                cantidad = self.cantidad_estudiantes(grupo)
                #Sumo la cantidad de estudiantes en el grupo a la cantidad total de estudiantes para el curso
                cantidad_total_estudiantes += cantidad
                #Calcular el porcentaje de asistencia
            cantidad_grupos = grupos_curso.count()
            datos.append((curso,grupos_curso,cantidad_total_estudiantes,cantidad_grupos))
        return datos
    
    def ejecutar(self):
        cursos= self.listar_cursos()
        datos= self.listar_grupos(cursos)
        return datos
    

    def anios_semestre(self):
        #Obtengo los años y semestres de los cursos del profesor    
        anios = Cursos.objects.filter(profesor_curso=self.__id_profesor).values('anio_curso', 'semestre_curso').distinct().order_by('-anio_curso', '-semestre_curso')
        return anios

    def buscar_cursos(self, nombre, anio='', semestre=''):
        #Obtengo los cursos del profesor que cumplan con los filtros de búsqueda (Nombre, año, semestre)
        nombre = '' if nombre is None else nombre
        anio = '' if anio is None else anio
        semestre = '' if semestre is None else semestre
        cursos = Cursos.objects.filter(profesor_curso=self.__id_profesor, nombre_curso__contains=nombre, anio_curso__contains=anio, semestre_curso__contains=semestre).order_by('-id_curso')
        datos = self.listar_grupos(cursos)
        return datos

    
            
from django.shortcuts import render, redirect
from .models import Excusa_falta_estudiante, Profesores, Cursos, Estudiantes, Grupos, Asistencia, Asistencia_estudiante,UserDevice
import plotly.graph_objects as go
import plotly.offline as opy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .funciones import informacion_cursos_estudiantes, crear_estudiantes, informacion_asistencia_grupo, actualizar_estudiantes, informacion_tomar_asistencia, informacion_perfil_profesor, informacion_perfil_estudiante, informacion_estudiante_profesor


# Create your views here.

#Cerrar sesión por medio de las funciones que brinda django y redirige al index
def cerrar_sesion(request):
    logout(request)
    return redirect('index')


def index(request):
    #Recibo todas las solicitudes POST (Formularios)
    if request.method == 'POST':
        #Verifico de qué formulario proviene la solicitud
        if 'inicioSesion' in request.POST:
            #Obtengo los datos del formulario
            rol = request.POST.get('rol')
            correo = request.POST.get('correo')
            contrasenia = request.POST.get('contrasenia')
            #Verifico si el usuario existe
            user = authenticate(request, username=correo, password=contrasenia)
            if user is not None:
                #Creo la sesión
                login(request, user)
                #Redirijo al usuario a su perfil (Profesor o estudiante)
                if rol == 'profesor' and Profesores.objects.filter(user=user).exists():
                    #Obtengo el profesor y guardo el ID en la sesión
                    profesor = Profesores.objects.get(user=user)
                    request.session['profesor_id'] = profesor.id
                    return redirect('cursos_estudiantes')
                elif rol == 'estudiante' and Estudiantes.objects.filter(user=user).exists():
                    #Obtengo la ip del cliente para registrar el dispositivo
                    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()  # obtén la dirección IP del usuario
                    print("ip",ip_address)
                    # Valido si la IP ya está registrada
                    validarIP= UserDevice.objects.filter(ip_address=ip_address).first()
                    print(validarIP)
                    # Valido si la IP ya está registrada y si es la misma del usuario
                    if not validarIP is None and validarIP.user != user:
                        # redirigo al index con un mensaje de error
                        return render(request, 'index.html', {'error': 'Ya inició sesión en otra cuenta, no puede iniciar sesión en dos cuentas el mismo día'})
                    else:
                        #Obtengo el profesor y guardo el ID en la sesión
                        estudiante= Estudiantes.objects.get(user=user)
                        request.session['estudiante_id'] = estudiante.id
                        # Register the IP address
                        UserDevice.objects.create(user=user, ip_address=ip_address)  # registra la dirección IP del usuario
                        return redirect('listar_grupos_estudiantes')
                else:
                    #En caso de que no se encuentre en la base de datos me devuelve a la página de inicio con un mensaje de error
                    return render(request, 'index.html', {'error': 'Usuario o contraseña incorrectos'})
            else:
                #En caso de que no se encuentre en la base de datos me devuelve a la página de inicio con un mensaje de error
                return render(request, 'index.html', {'error': 'Usuario o contraseña incorrectos'})
            
        elif 'registro' in request.POST:
            #Obtengo los datos del formulario
            documento = request.POST.get('documento')
            nombres = request.POST.get('nombres')
            apellidos = request.POST.get('apellidos')
            correo = request.POST.get('correo')
            contrasenia = request.POST.get('contrasenia')
            #Creo el usuario
            if User.objects.filter(username=correo).exists():
                if Profesores.objects.filter(user__username=correo).exists():
                    return render(request, 'index.html', {'error_registro': 'El correo ya está en uso'})
                else:
                    user= User.objects.get(username=correo)
            else:
                user= User.objects.create_user(username=correo, email=correo, password=contrasenia)
            #Creo el estudiante. Siempre por defecto se va a crear como estudiante, el rol lo cambia es el administrador
            Profesores.objects.create(
                user= user,
                documento_profesor = documento,
                nombres_profesor = nombres,
                apellidos_profesor = apellidos,
            )

    return render(request, 'index.html')

#Vistas para listar los cursos de los profesores
@login_required
def cursos_estudiantes(request):
    #Valido si el usuario tiene una sesión activa como profesor
    if  'profesor_id' in request.session:
        #Obtengo los datos del profesor    
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        #Creo una instancia de la clase que me permite obtener la información de los cursos
        listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
        #Obtengo la información de los cursos
        datos= listar_cursos.ejecutar()
        #Obtengo los semestres
        semestres= listar_cursos.anios_semestre()
        #Valido si se envió un formulario
        if request.method == 'POST':
            #Valido si se envió el formulario de busqueda
            if 'buscar_cursos' in request.POST:
                #Obtengo el semestre y el nombre del curso
                periodo = request.POST.get('semestre')
                nombre_curso= request.POST.get('nombre_curso')
                #Valido si se envió el semestre
                if periodo:
                    #Obtengo el semestre y el año y busco los cursos que coincidan con el nombre y el semestre
                    semestre = periodo.split('-')[1]
                    anio_curso = periodo.split('-')[0]
                    datos= listar_cursos.buscar_cursos(nombre_curso,anio_curso, semestre)
                else:
                    #Busco los cursos que coincidan con el nombre
                    datos= listar_cursos.buscar_cursos(nombre_curso)                
                return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor})

            elif 'crearCurso' in request.POST:

                try:
                    #Obtengo los datos del formulario
                    nombre_curso = request.POST.get('nombre_curso')
                    anio_curso = request.POST.get('anio_curso')
                    semestre_curso = request.POST.get('semestre_curso')
                    #Obtengo el profesor
                    profesor = Profesores.objects.get(id=request.session['profesor_id'])
                    #Creo el curso
                    curso = Cursos.objects.create(
                        nombre_curso = nombre_curso,
                        anio_curso = anio_curso,
                        semestre_curso = semestre_curso,
                        profesor_curso = profesor
                    )
                    #Obtengo el número del grupo
                    numero_grupo = request.POST.get('grupo_curso')
                    #Creo el grupo
                    grupo = Grupos.objects.create(
                        nombre_grupo = numero_grupo,
                        curso_grupo = curso
                    )
                    #Obtengo el archivo con los estudiantes
                    archivo = request.FILES['listaEstudiantes_curso']
                    #Función que edita el archivo del SIA, inserta los estudiantes en la base de datos y los asigna al grupo
                    agregar_estudiantes= crear_estudiantes.Crear_grupo_estudiantes(archivo, grupo.id_grupo)
                    agregar_estudiantes.ejecutar()
                    return redirect('cursos_estudiantes')

                #En caso de algún error, se redirige a la página de cursos con un mensaje de error
                except Exception as e:
                    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                    datos= listar_cursos.ejecutar()
                    return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor,'error': f'No se pudo crear el curso: {str(e)}'})
            
            elif 'crearGrupo' in request.POST:

                try:
                    #Obtengo los datos del formulario
                    curso_id = request.POST.get('codigoCurso')
                    #Consulto el curso
                    curso = Cursos.objects.get(id_curso=curso_id)
                    numero_grupo = request.POST.get('numero_grupo')
                    #Creo el grupo
                    grupo = Grupos.objects.create(
                        nombre_grupo = numero_grupo,
                        curso_grupo = curso
                    )
                    #Obtengo el archivo con los estudiantes
                    archivo = request.FILES['listaEstudiantes']
                    #Función que edita el archivo del SIA, inserta los estudiantes en la base de datos y los asigna al grupo
                    agregar_estudiantes= crear_estudiantes.Crear_grupo_estudiantes(archivo, grupo.id_grupo)
                    agregar_estudiantes.ejecutar()
                    return redirect('cursos_estudiantes')
                
                #En caso de algún error, se redirige a la página de cursos con un mensaje de error
                except Exception as e:
                    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                    datos= listar_cursos.ejecutar()
                    return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor,'error': f'No se pudo crear el grupo: {str(e)}'})
            
            #Creo un para tener el post de cada curso y poder realizar las acciones
            for i in datos:
                #Valido si se envió el formulario para ver la información del curso
                if f'info_{i[0].id_curso}' in request.POST:

                    try:
                        #Obtengo el id del grupo
                        id_grupo = request.POST.get('grupo')
                        grupo= Grupos.objects.get(id_grupo=id_grupo)
                        if grupo is not None:
                            #Redirijo a la página de información del curso
                            return redirect('informacion_curso',  grupo=grupo.id_grupo)
                        else:
                            return redirect('cursos_estudiantes')
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')
                
                #Valido si se envió el formulario para eliminar el curso
                elif f'eliminar_curso_{i[0].id_curso}' in request.POST:
                    try:
                        #Elimino el curso con todos los grupos y todo lo relacionado
                        curso= Cursos.objects.get(id_curso=i[0].id_curso)
                        curso.delete()
                        return redirect('cursos_estudiantes')
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')

                #Valido si se envió el formulario para editar el curso
                elif f'editar_curso_{i[0].id_curso}' in request.POST:

                    try:
                        #Obtengo los datos del curso
                        curso_id = request.POST.get('codigoCurso')
                        curso = Cursos.objects.get(id_curso=curso_id)
                        nombre_curso = request.POST.get('nombre_curso')
                        anio_curso = request.POST.get('anio_curso')
                        semestre_curso = request.POST.get('semestre_curso')
                        curso.nombre_curso = nombre_curso
                        curso.anio_curso = anio_curso
                        curso.semestre_curso = semestre_curso
                        #Guardo los cambios
                        curso.save()
                        return redirect('cursos_estudiantes')
                        
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')

        #En caso de que la solicitud sea GET
        else:
            listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
            datos= listar_cursos.ejecutar()
            return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor})

    #En caso de que no tenga una sesión activa como profesor redirijo al index
    return redirect('index')
    

@login_required
def informacion_curso(request, grupo):
    #Valido si el usuario tiene una sesión activa como profesor
    if  'profesor_id' in request.session:
        #Obtengo los datos del profesor
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        #Valido si el grupo existe
        if Grupos.objects.filter(id_grupo=grupo).exists():
            #Obtengo el grupo y listo la información de las asistencias y el gráfico
            grupo = Grupos.objects.get(id_grupo=grupo)
            listar_asistencia= informacion_asistencia_grupo.informacion_listado_asistencia(grupo.id_grupo)
            datos,graph= listar_asistencia.ejecutar()

            #Valido si se envió un formulario
            if request.method == 'POST':

                if 'VerEstudiantes' in request.POST:
                    #Redirijo a la página que lista los estudiantes
                    return redirect('listar_estudiantes_curso',grupo=grupo.id_grupo)
                
                elif 'buscar_asistencia' in request.POST:
                    #Busca Asistencia por fecha
                    fecha = request.POST.get('fecha_asistencia')
                    datos_buscados= listar_asistencia.buscar_asistencia(fecha)
                    return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos_buscados,'graph':graph})


                elif 'crearAsistencia' in request.POST:

                    try:
                        #Crea una asistencia con activo=False y vincula a los estudiantes a esa asistencia pero por defecto registro_Asistencia es False
                        fecha = request.POST.get('fecha')
                        asistencia= Asistencia.objects.create(
                            fecha_asistencia=fecha,
                            grupo=grupo
                        )
                        Asistencia_estudiante.objects.bulk_create([Asistencia_estudiante(asistencia=asistencia,estudiante=estudiante) for estudiante in grupo.estudiantes_grupo.filter(inscripcion__estado=True)])
                        return redirect('tomar_asistencia', asistencia=asistencia.id_asistencia)
                        
                    except Exception as e:
                        #En caso de error redirijo a la página de información del curso
                        print(e)
                        return redirect('informacion_curso', grupo=grupo.id_grupo)

                
                elif 'actualizar_grupo' in request.POST:

                    try:
                        #Actualiza el nombre del grupo
                        nuevo_nombre_grupo = request.POST.get('nuevo_nombre_grupo')
                        grupo.nombre_grupo = nuevo_nombre_grupo
                        grupo.save()
                        return redirect('informacion_curso', grupo=grupo.id_grupo)
                    
                    except Exception as e:
                        print(e)
                        return redirect('informacion_curso', grupo=grupo.id_grupo)

                elif 'eliminar_grupo' in request.POST:

                    try:
                        #Elimina el grupo y todo lo relacionado
                        grupo.delete()
                        return redirect('cursos_estudiantes')
                    
                    except Exception as e:
                        print(e)
                        return redirect('cursos_estudiantes')
                
                #Creo un ciclo para tener el post de cada asistencia y poder realizar las acciones
                for i in datos:
                    if f'info_{i[0].id_asistencia}' in request.POST:
                        try:
                            return redirect('tomar_asistencia',  asistencia=i[0].id_asistencia)
                        except Exception as e:
                            print(e)
                            return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos, 'graph':graph})

            #Método get   
            else:
                #envio la información de las asistencias y el gráfico
                return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos, 'graph':graph})
        else:
            #En caso de que el grupo no exista redirijo a la página de cursos
            return redirect('cursos_estudiantes')
    else:
        #En caso de que no tenga una sesión activa como profesor redirijo al index
        return redirect('index')

@login_required
def listar_estudiantes_curso(request,grupo):
    #Valido si el usuario tiene una sesión activa como profesor
    if  'profesor_id' in request.session:
        #Obtengo los datos del profesor y el grupo
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        grupo = Grupos.objects.get(id_grupo=grupo)

        try: 
            if request.method == 'POST':

                if 'actualizarEstudiantes' in request.POST:
                    #Obtengo el archivo con los estudiantes y actualizo el grupo validando nuevos y estudiantes eliminados (Inactivos)
                    archivo = request.FILES['archivo_estudiantes']
                    actualizar = actualizar_estudiantes.actualizar_grupo_estudiantes(archivo, grupo.id_grupo)
                    cantidad=actualizar.ejecutar()
                    estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True).order_by('apellidos_estudiante')
                    estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False).order_by('apellidos_estudiante')
                    return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'mensaje_actualizacion': f'Estudiantes actualizados: {cantidad[0]} estudiantes nuevos, {cantidad[1]} estudiantes eliminados'})
                
                elif 'buscar_estudiante' in request.POST:
                    #Busca estudiantes por documento
                    documento = request.POST.get('documento')
                    documento= '' if documento is None else documento
                    estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True, documento_estudiante__startswith=documento).order_by('apellidos_estudiante')
                    estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False, documento_estudiante__startswith=documento).order_by('apellidos_estudiante')
                    return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos})

            else:
                #Listo los estudiantes activos e inactivos
                estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True).order_by('apellidos_estudiante')
                estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False).order_by('apellidos_estudiante')
                return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos})

        except Exception as e:
            print(e)
            return redirect('informacion_curso',grupo=grupo.id_grupo)
    else:
        #En caso de que no tenga una sesión activa como profesor redirijo al index
        return redirect('index')

@login_required
def tomar_asistencia(request,asistencia):
    #Valido si el usuario tiene una sesión activa como profesor
    if  'profesor_id' in request.session:
        #Obtengo los datos del profesor y la asistencia
        asistencia = Asistencia.objects.get(id_asistencia=asistencia)
        profesor = Profesores.objects.get(id=request.session['profesor_id'])

        if request.method == 'POST': 

            if 'buscar_estudiante_ausente' in request.POST:
                #Busca estudiantes ausentes por documento
                listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
                documento= request.POST.get('documento')
                grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.buscar_estudiante_ausente(documento)
                return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})

            elif 'buscar_estudiante_presente' in request.POST:
                #Busca estudiantes presentes por documento
                listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
                documento= request.POST.get('documento')
                grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.buscar_estudiante_presente(documento)
                return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})

            elif 'cambiar_estado' in request.POST:
                #Cambia el estado de la asistencia para permitir o no el registro de asistencia
                asistencia.activa= not asistencia.activa
                asistencia.save()
                return redirect('tomar_asistencia',asistencia=asistencia.id_asistencia)
            
            #Creo un ciclo para tener el post de cada falta por estudiante y poder realizar las acciones
            excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=asistencia)
            for i in excusa_falta:
                if f'aceptar_excusa_{i.id_excusa}' in request.POST:
                    #Acepta la excusa
                    i.excusa_valida=True
                    i.save()
                    estudiante= request.POST.get('id_estudiante')
                    #Obtengo la asistencia, registro la asistencia y la excusa
                    asignar_asistencia = Asistencia_estudiante.objects.get(estudiante=estudiante, asistencia=asistencia)
                    asignar_asistencia.excusa=True
                    asignar_asistencia.registro_Asistencia=True    
                    asignar_asistencia.save()
                    return redirect('tomar_asistencia',asistencia=asistencia.id_asistencia)
        else:
            #Listo los estudiantes y las excusas para el caso del método GET
            listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
            grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.listar_asistencia()
            return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})
    else:
        #En caso de que no tenga una sesión activa como profesor redirijo al index
        return redirect('index')
    
    #Caso en el que no coincida con ningún post
    return render(request, 'profesores/tomar_asistencia.html')

@login_required
def perfil_profesor(request):
    #Valido si el usuario tiene una sesión activa como profesor
    if  'profesor_id' in request.session:
        #Obtengo los datos del profesor, semestres y la información de las asistencias
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        informacion= informacion_perfil_profesor.informacion_profesor(profesor.id)
        datos_profesor= informacion.datos_profesor()
        semestres= informacion.semestres()
        informacion_asistencia = informacion.listar_asistencia()

        if request.method == 'POST':

            if 'cambiar_contrasenia' in request.POST:
                #Cambia la contraseña del profesor
                contrasenia = request.POST.get('contrasenia')
                informacion.editar_contrasenia(contrasenia)
                return redirect('perfil_profesor')
            
            if 'ver_grafica_semestre' in request.POST:
                #Crea la gráfica del semestre seleccionado
                datos_semestre= request.POST.get('semestre_curso')
                graph = informacion.crear_grafica_total(datos_semestre)
                return render(request, 'profesores/perfil_profesor.html', {'profesor': profesor, 'datos_profesor':datos_profesor, 'semestres': semestres, 'informacion_asistencia':informacion_asistencia, 'graph': graph})
        

        #Crea la gráfica del semestre actual
        graph = informacion.crear_grafica_total()
        return render(request, 'profesores/perfil_profesor.html', {'profesor': profesor, 'datos_profesor':datos_profesor, 'semestres': semestres, 'informacion_asistencia':informacion_asistencia, 'graph': graph})

    else:
        #En caso de que no tenga una sesión activa como profesor redirijo al index
        return redirect('index')


    # Crear gráfico

@login_required
def informacion_estudiante(request,id_estudiante):
    #Valido si el usuario tiene una sesión activa como profesor
    if 'profesor_id' in request.session:
        #Obtengo los datos del profesor, el estudiante y listo la información de las asistencias
        profesor= Profesores.objects.get(id=request.session['profesor_id'])
        estudiante= Estudiantes.objects.get(id=id_estudiante)
        informacion= informacion_estudiante_profesor.informacion_estudiante(estudiante.id)
        informacion_asistencia= informacion.listar_asistencia(profesor.id)
        return render(request, 'profesores/informacion_estudiante.html', {'profesor': profesor, 'datos_estudiante': estudiante, 'informacion_asistencia':informacion_asistencia})
    else:
        return redirect('index')



#Vistas para estudiantes

@login_required
def listar_grupos_estudiantes(request):
    #Valido si el usuario tiene una sesión activa como estudiante
    if  'estudiante_id' in request.session:
        #Obtengo los datos del estudiante, del grupo y de los semestres
        estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
        grupos = Grupos.objects.filter(estudiantes_grupo=estudiante).order_by('-id_grupo')
        semestres = Grupos.objects.filter(estudiantes_grupo=estudiante).values('curso_grupo__anio_curso', 'curso_grupo__semestre_curso').distinct().order_by('-curso_grupo__anio_curso', '-curso_grupo__semestre_curso')

        #Valido si se envió un formulario por medio de un ciclo que recoje el post de cada grupo
        for i in grupos:
            if f'info_{i.id_grupo}' in request.POST:
                try:
                    #Redirijo a la página donde lista las asistencias del grupo
                    return redirect('registrar_asistencia',  grupo=i.id_grupo)
                except Exception as e:
                    print(e)
                    return render(request, 'estudiantes/cursos_estudiante.html', {'grupos': grupos, 'estudiante': estudiante, 'semestres': semestres})
        
        if 'buscar_curso' in request.POST:
            #Busqueda de curso por semestre y nombre
            periodo = request.POST.get('semestre')
            nombre_curso= request.POST.get('nombre_curso')
            if periodo:
                semestre = periodo.split('-')[1]
                anio_curso = periodo.split('-')[0]
                grupos = Grupos.objects.filter(estudiantes_grupo=estudiante, curso_grupo__nombre_curso__icontains=nombre_curso,curso_grupo__semestre_curso=semestre,curso_grupo__anio_curso=anio_curso).order_by('-id_grupo')
            else:      
                grupos = Grupos.objects.filter(estudiantes_grupo=estudiante, curso_grupo__nombre_curso__icontains=nombre_curso).order_by('-id_grupo')

        return render(request, 'estudiantes/cursos_estudiante.html', {'grupos': grupos, 'estudiante': estudiante, 'semestres': semestres})
    else:
        return redirect('index')
    
@login_required
def registrar_asistencia(request,grupo):
    #Valido si el usuario tiene una sesión activa como estudiante
    if  'estudiante_id' in request.session:
        #Obtengo los datos del estudiante, del grupo y de la asistencia
        estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
        grupo = Grupos.objects.get(id_grupo=grupo)
        asistencia = Asistencia_estudiante.objects.filter(estudiante=estudiante, asistencia__grupo=grupo)

        if request.method == 'POST':

            #Busqueda de asistencia por fecha
            if 'buscar_asistencia' in request.POST:
                fecha = request.POST.get('fecha_asistencia')
                asistencia = Asistencia_estudiante.objects.filter(estudiante=estudiante, asistencia__grupo=grupo, asistencia__fecha_asistencia=fecha)
                return render(request, 'estudiantes/registrar_asistencia.html', {'grupo': grupo, 'estudiante': estudiante, 'asistencias': asistencia})

            #Creo un ciclo para tener el post de cada asistencia y poder realizar las acciones
            for i in asistencia:

                if f'registar_{i.id_asistencia_estudiante}' in request.POST:
                    #Registro de asistencia
                    asistencia_estudiante= Asistencia_estudiante.objects.get(id_asistencia_estudiante=i.id_asistencia_estudiante)
                    asistencia_estudiante.registro_Asistencia=True
                    asistencia_estudiante.save()
                    return redirect('registrar_asistencia', grupo=grupo.id_grupo)

                elif f'enviar_excusa_{i.id_asistencia_estudiante}' in request.POST:
                    #Envío de excusa en caso de que el estudiante la presente, se guarda la excusa y el soporte
                    excusa = request.POST.get('justificacion')
                    soporte = request.FILES.get('documento_soporte', None)
                    excusa_estudiante= Excusa_falta_estudiante.objects.create(
                        motivo=excusa,
                        soporte_excusa=soporte,
                        estudiante=estudiante,
                        asistencia_estudiante=i
                    )
                    #Para los casos en los que tenga excusa, se registra la excusa en la asistencia (Todavía no se está usando pero sirve para posterior información)
                    i.excusa=True
                    i.save()
                    return redirect('registrar_asistencia', grupo=grupo.id_grupo)
                
                if request.POST:
                    #En caso de que no se haya seleccionado ninguna opción
                    return redirect('registrar_asistencia', grupo=grupo.id_grupo)
                    
        else:
            return render(request, 'estudiantes/registrar_asistencia.html', {'grupo': grupo, 'estudiante': estudiante, 'asistencias': asistencia})
    else:
        return redirect('index')

@login_required
def perfil_estudiante(request):
    #Valido si el usuario tiene una sesión activa como estudiante
    if 'estudiante_id' in request.session:
        #Obtengo los datos del estudiante y de la información de las asistencias
        estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
        informacion= informacion_perfil_estudiante.informacion_estudiante(estudiante.id)
        datos_estudiante= informacion.datos_estudiante()
        informacion_asistencia,periodo = informacion.listar_asistencia()
        return render(request, 'estudiantes/perfil_estudiante.html', {'estudiante': estudiante, 'datos_estudiante':datos_estudiante, 'informacion_asistencia':informacion_asistencia, 'periodo': periodo})
    else:
        return redirect('index')


from django.shortcuts import render, redirect
from .models import Excusa_falta_estudiante, Profesores, Cursos, Estudiantes, Grupos, Asistencia, Asistencia_estudiante,UserDevice
import plotly.graph_objects as go
import plotly.offline as opy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .funciones import informacion_cursos_estudiantes, crear_estudiantes, informacion_asistencia_grupo, actualizar_estudiantes, informacion_tomar_asistencia, informacion_perfil_profesor, informacion_perfil_estudiante, informacion_estudiante_profesor


# Create your views here.

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
                    ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()  # obtén la dirección IP del usuario
                    print("ip",ip_address)
                    # Check if there is already a record with the same IP address
                    validarIP= UserDevice.objects.filter(ip_address=ip_address).first()
                    if validarIP and validarIP.user != user:
                        # Close the session and redirect to the index page
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

@login_required
def cursos_estudiantes(request):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
        datos= listar_cursos.ejecutar()
        semestres= listar_cursos.anios_semestre()
        if request.method == 'POST':
            
            if 'buscar_cursos' in request.POST:
                periodo = request.POST.get('semestre')
                nombre_curso= request.POST.get('nombre_curso')
                if periodo:
                    semestre = periodo.split('-')[1]
                    anio_curso = periodo.split('-')[0]
                    datos= listar_cursos.buscar_cursos(nombre_curso,anio_curso, semestre)
                else:
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
                    archivo = request.FILES['listaEstudiantes_curso']
                    agregar_estudiantes= crear_estudiantes.Crear_grupo_estudiantes(archivo, grupo.id_grupo)
                    agregar_estudiantes.ejecutar()
                    return redirect('cursos_estudiantes')

                except Exception as e:
                    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                    datos= listar_cursos.ejecutar()
                    return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor,'error': f'No se pudo crear el curso: {str(e)}'})
            
            elif 'crearGrupo' in request.POST:
                try:
                    curso_id = request.POST.get('codigoCurso')
                    print(curso_id)
                    curso = Cursos.objects.get(id_curso=curso_id)
                    numero_grupo = request.POST.get('numero_grupo')
                    #Creo el grupo
                    grupo = Grupos.objects.create(
                        nombre_grupo = numero_grupo,
                        curso_grupo = curso
                    )
                    archivo = request.FILES['listaEstudiantes']
                    agregar_estudiantes= crear_estudiantes.Crear_grupo_estudiantes(archivo, grupo.id_grupo)
                    agregar_estudiantes.ejecutar()
                    return redirect('cursos_estudiantes')

                except Exception as e:
                    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                    datos= listar_cursos.ejecutar()
                    return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor,'error': f'No se pudo crear el grupo: {str(e)}'})
            for i in datos:
                if f'info_{i[0].id_curso}' in request.POST:
                    try:
                        id_grupo = request.POST.get('grupo')
                        grupo= Grupos.objects.get(id_grupo=id_grupo)
                        if grupo is not None:
                            return redirect('informacion_curso',  grupo=grupo.id_grupo)
                        else:
                            return redirect('cursos_estudiantes')
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')
                elif f'eliminar_curso_{i[0].id_curso}' in request.POST:
                    try:
                        curso= Cursos.objects.get(id_curso=i[0].id_curso)
                        curso.delete()
                        return redirect('cursos_estudiantes')
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')

                elif f'editar_curso_{i[0].id_curso}' in request.POST:
                    try:
                        curso_id = request.POST.get('codigoCurso')
                        curso = Cursos.objects.get(id_curso=curso_id)
                        nombre_curso = request.POST.get('nombre_curso')
                        anio_curso = request.POST.get('anio_curso')
                        semestre_curso = request.POST.get('semestre_curso')
                        curso.nombre_curso = nombre_curso
                        curso.anio_curso = anio_curso
                        curso.semestre_curso = semestre_curso
                        curso.save()
                        return redirect('cursos_estudiantes')
                        
                    except Exception as e:
                        print(e)
                        redirect('cursos_estudiantes')


        else:
            if 'profesor_id' in request.session:
                listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                datos= listar_cursos.ejecutar()
                return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor})
            else:
                return redirect('index')
    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
    datos= listar_cursos.ejecutar()
    return render(request, 'profesores/cursos_estudiantes.html', {'cursos': datos,'semestres':semestres ,'profesor': profesor})

@login_required
def informacion_curso(request, grupo):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        if Grupos.objects.filter(id_grupo=grupo).exists():
            grupo = Grupos.objects.get(id_grupo=grupo)
            listar_asistencia= informacion_asistencia_grupo.informacion_listado_asistencia(grupo.id_grupo)
            datos,graph= listar_asistencia.ejecutar()
            if request.method == 'POST':
                if 'VerEstudiantes' in request.POST:
                    return redirect('listar_estudiantes_curso',grupo=grupo.id_grupo)
                
                elif 'buscar_asistencia' in request.POST:
                    fecha = request.POST.get('fecha_asistencia')
                    datos_buscados= listar_asistencia.buscar_asistencia(fecha)
                    return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos_buscados,'graph':graph})


                elif 'crearAsistencia' in request.POST:
                    fecha = request.POST.get('fecha')
                    asistencia= Asistencia.objects.create(
                        fecha_asistencia=fecha,
                        grupo=grupo
                    )
                    asistencia_estudiante= Asistencia_estudiante.objects.bulk_create([Asistencia_estudiante(asistencia=asistencia,estudiante=estudiante) for estudiante in grupo.estudiantes_grupo.filter(inscripcion__estado=True)])
                    return redirect('tomar_asistencia', asistencia=asistencia.id_asistencia)

                
                elif 'actualizar_grupo' in request.POST:
                    try:
                        nuevo_nombre_grupo = request.POST.get('nuevo_nombre_grupo')
                        grupo.nombre_grupo = nuevo_nombre_grupo
                        grupo.save()
                        return redirect('informacion_curso', grupo=grupo.id_grupo)
                    except Exception as e:
                        print(e)
                        return redirect('informacion_curso', grupo=grupo.id_grupo)

                elif 'eliminar_grupo' in request.POST:
                    print('eliminar')
                    try:
                        grupo.delete()
                        return redirect('cursos_estudiantes')
                    except Exception as e:
                        print(e)
                        return redirect('cursos_estudiantes')
                
                for i in datos:
                    if f'info_{i[0].id_asistencia}' in request.POST:
                        try:
                            return redirect('tomar_asistencia',  asistencia=i[0].id_asistencia)
                        except Exception as e:
                            print(e)
                            return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos, 'graph':graph})
                    
            else:
                return render(request, 'profesores/informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos, 'graph':graph})
        else:
            return redirect('cursos_estudiantes')
    else:
        return redirect('index')

@login_required
def listar_estudiantes_curso(request,grupo):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        grupo = Grupos.objects.get(id_grupo=grupo)
        try: 
            if request.method == 'POST':
                if 'actualizarEstudiantes' in request.POST:
                    archivo = request.FILES['archivo_estudiantes']
                    actualizar = actualizar_estudiantes.actualizar_grupo_estudiantes(archivo, grupo.id_grupo)
                    cantidad=actualizar.ejecutar()
                    estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True).order_by('apellidos_estudiante')
                    estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False).order_by('apellidos_estudiante')
                    return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'mensaje_actualizacion': f'Estudiantes actualizados: {cantidad[0]} estudiantes nuevos, {cantidad[1]} estudiantes eliminados'})
                
                elif 'buscar_estudiante' in request.POST:
                    documento = request.POST.get('documento')
                    documento= '' if documento is None else documento
                    estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True, documento_estudiante__startswith=documento).order_by('apellidos_estudiante')
                    estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False, documento_estudiante__startswith=documento).order_by('apellidos_estudiante')
                    return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos})

            else:
                estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True).order_by('apellidos_estudiante')
                estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False).order_by('apellidos_estudiante')
                return render(request, 'profesores/listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos})

        except Exception as e:
            print(e)
            return redirect('informacion_curso',grupo=grupo.id_grupo)
    else:
        return redirect('index')

@login_required
def tomar_asistencia(request,asistencia):
    if  'profesor_id' in request.session:
        asistencia = Asistencia.objects.get(id_asistencia=asistencia)
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        if request.method == 'POST': 

            if 'buscar_estudiante_ausente' in request.POST:
                listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
                documento= request.POST.get('documento')
                grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.buscar_estudiante_ausente(documento)
                return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})

            elif 'buscar_estudiante_presente' in request.POST:
                listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
                documento= request.POST.get('documento')
                grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.buscar_estudiante_presente(documento)
                return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})

            elif 'cambiar_estado' in request.POST:
                asistencia.activa= not asistencia.activa
                asistencia.save()
                return redirect('tomar_asistencia',asistencia=asistencia.id_asistencia)
            excusa_falta = Excusa_falta_estudiante.objects.filter(asistencia_estudiante__asistencia=asistencia)
            for i in excusa_falta:
                if f'aceptar_excusa_{i.id_excusa}' in request.POST:
                    i.excusa_valida=True
                    i.save()
                    estudiante= request.POST.get('id_estudiante')
                    asignar_asistencia = Asistencia_estudiante.objects.get(estudiante=estudiante, asistencia=asistencia)
                    asignar_asistencia.excusa=True
                    asignar_asistencia.registro_Asistencia=True    
                    asignar_asistencia.save()
                    return redirect('tomar_asistencia',asistencia=asistencia.id_asistencia)
        else:
            listar= informacion_tomar_asistencia.informacion_listado_tomar_asistencia(asistencia.id_asistencia)
            grupo,estudiantes_activos,estudiantes_inactivos, fecha, estado_asistencia, excusa_falta = listar.listar_asistencia()
            return render(request, 'profesores/tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha, 'estado_asistencia': estado_asistencia, 'excusas': excusa_falta})
    else:
        return redirect('index')
    return render(request, 'profesores/tomar_asistencia.html')

@login_required
def perfil_profesor(request):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        informacion= informacion_perfil_profesor.informacion_profesor(profesor.id)
        datos_profesor= informacion.datos_profesor()
        semestres= informacion.semestres()
        informacion_asistencia = informacion.listar_asistencia()

        if request.method == 'POST':
            if 'cambiar_contrasenia' in request.POST:
                contrasenia = request.POST.get('contrasenia')
                informacion.editar_contrasenia(contrasenia)
                return redirect('perfil_profesor')
            
            if 'ver_grafica_semestre' in request.POST:
                datos_semestre= request.POST.get('semestre_curso')
                print('semestre',datos_semestre)
                graph = informacion.crear_grafica_total(datos_semestre)
                return render(request, 'profesores/perfil_profesor.html', {'profesor': profesor, 'datos_profesor':datos_profesor, 'semestres': semestres, 'informacion_asistencia':informacion_asistencia, 'graph': graph})
        


        graph = informacion.crear_grafica_total()
        return render(request, 'profesores/perfil_profesor.html', {'profesor': profesor, 'datos_profesor':datos_profesor, 'semestres': semestres, 'informacion_asistencia':informacion_asistencia, 'graph': graph})

    else:
        return redirect('index')


    # Crear gráfico

def informacion_estudiante(request,id_estudiante):
    profesor= Profesores.objects.get(id=request.session['profesor_id'])
    estudiante= Estudiantes.objects.get(id=id_estudiante)
    informacion= informacion_estudiante_profesor.informacion_estudiante(estudiante.id)
    informacion_asistencia= informacion.listar_asistencia(profesor.id)
    return render(request, 'profesores/informacion_estudiante.html', {'profesor': profesor, 'datos_estudiante': estudiante, 'informacion_asistencia':informacion_asistencia})

    



#Vistas para estudiantes

@login_required
def listar_grupos_estudiantes(request):
    if  'estudiante_id' in request.session:
        estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
        grupos = Grupos.objects.filter(estudiantes_grupo=estudiante).order_by('-id_grupo')
        semestres = Grupos.objects.filter(estudiantes_grupo=estudiante).values('curso_grupo__anio_curso', 'curso_grupo__semestre_curso').distinct().order_by('-curso_grupo__anio_curso', '-curso_grupo__semestre_curso')

        for i in grupos:
            if f'info_{i.id_grupo}' in request.POST:
                try:
                    return redirect('registrar_asistencia',  grupo=i.id_grupo)
                except Exception as e:
                    print(e)
                    return render(request, 'estudiantes/cursos_estudiante.html', {'grupos': grupos, 'estudiante': estudiante, 'semestres': semestres})
        
        if 'buscar_curso' in request.POST:
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
    if  'estudiante_id' in request.session:
        estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
        grupo = Grupos.objects.get(id_grupo=grupo)
        asistencia = Asistencia_estudiante.objects.filter(estudiante=estudiante, asistencia__grupo=grupo)
        if request.method == 'POST':

            if 'buscar_asistencia' in request.POST:
                fecha = request.POST.get('fecha_asistencia')
                asistencia = Asistencia_estudiante.objects.filter(estudiante=estudiante, asistencia__grupo=grupo, asistencia__fecha_asistencia=fecha)
                return render(request, 'estudiantes/registrar_asistencia.html', {'grupo': grupo, 'estudiante': estudiante, 'asistencias': asistencia})

            for i in asistencia:
                if f'registar_{i.id_asistencia_estudiante}' in request.POST:
                    asistencia_estudiante= Asistencia_estudiante.objects.get(id_asistencia_estudiante=i.id_asistencia_estudiante)
                    asistencia_estudiante.registro_Asistencia=True
                    asistencia_estudiante.save()
                    return redirect('registrar_asistencia', grupo=grupo.id_grupo)

                elif f'enviar_excusa_{i.id_asistencia_estudiante}' in request.POST:
                    excusa = request.POST.get('justificacion')
                    soporte = request.FILES.get('documento_soporte', None)
                    excusa_estudiante= Excusa_falta_estudiante.objects.create(
                        motivo=excusa,
                        soporte_excusa=soporte,
                        estudiante=estudiante,
                        asistencia_estudiante=i
                    )
                    i.excusa=True
                    i.save()
                    return redirect('registrar_asistencia', grupo=grupo.id_grupo)
                    
        else:
            return render(request, 'estudiantes/registrar_asistencia.html', {'grupo': grupo, 'estudiante': estudiante, 'asistencias': asistencia})
    else:
        return redirect('index')
    return render(request, 'estudiantes/registrar_asistencia.html')

@login_required
def perfil_estudiante(request):
    estudiante = Estudiantes.objects.get(id=request.session['estudiante_id'])
    informacion= informacion_perfil_estudiante.informacion_estudiante(estudiante.id)
    datos_estudiante= informacion.datos_estudiante()
    informacion_asistencia,periodo = informacion.listar_asistencia()
    return render(request, 'estudiantes/perfil_estudiante.html', {'estudiante': estudiante, 'datos_estudiante':datos_estudiante, 'informacion_asistencia':informacion_asistencia, 'periodo': periodo})


from django.shortcuts import render, redirect
from .models import Profesores, Cursos, Estudiantes, Grupos, Asistencia, Asistencia_estudiante
import plotly.graph_objects as go
import plotly.offline as opy
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .funciones import informacion_cursos_estudiantes, crear_estudiantes, informacion_asistencia_grupo, actualizar_estudiantes


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
                    #Obtengo el profesor y guardo el ID en la sesión
                    estudiante= Estudiantes.objects.get(user=user)
                    request.session['estudiante_id'] = estudiante.id
                    return redirect('cursos_estudiantes')
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
                return render(request, 'index.html', {'error_registro': 'El correo ya está en uso'})
            user= User.objects.create_user(username=correo, email=correo, password=contrasenia)
            #Creo el estudiante. Siempre por defecto se va a crear como estudiante, el rol lo cambia es el administrador
            Estudiantes.objects.create(
                user= user,
                documento_estudiante = documento,
                nombres_estudiante = nombres,
                apellidos_estudiante = apellidos,
            )

    return render(request, 'index.html')

@login_required
def cursos_estudiantes(request):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
        datos= listar_cursos.ejecutar()
        if request.method == 'POST':
            print(request.POST)
            if 'crearCurso' in request.POST:
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
                    return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor, 'exito': 'Curso creado exitosamente'})

                except Exception as e:
                    listar_cursos= informacion_cursos_estudiantes.informacion_listado_cursos(request.session['profesor_id'])
                    datos= listar_cursos.ejecutar()
                    return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor,'error': f'No se pudo crear el curso: {str(e)}'})
            
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
                    return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor, 'exito': 'Curso creado exitosamente'})

                except Exception as e:
                    return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor,'error': f'No se pudo crear el grupo: {str(e)}'})
            for i in datos:
                if f'info_{i[0].id_curso}' in request.POST:
                    try:
                        id_grupo = request.POST.get('grupo')
                        grupo= Grupos.objects.get(id_grupo=id_grupo)
                        return redirect('informacion_curso',  grupo=grupo.id_grupo)
                    except Exception as e:
                        print(e)
                        return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor})
        else:
            if 'profesor_id' in request.session:
                return render(request, 'cursos_estudiantes.html', {'cursos': datos,'profesor': profesor})
    
    return redirect('index')

@login_required
def informacion_curso(request, grupo):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        if Grupos.objects.filter(id_grupo=grupo).exists():
            grupo = Grupos.objects.get(id_grupo=grupo)
            listar_asistencia= informacion_asistencia_grupo.informacion_listado_asistencia(grupo.id_grupo)
            datos= listar_asistencia.ejecutar()
            if request.method == 'POST':
                if 'VerEstudiantes' in request.POST:
                    return redirect('listar_estudiantes_curso',grupo=grupo.id_grupo)
                elif 'crearAsistencia' in request.POST:
                    fecha = request.POST.get('fecha')
                    asistencia= Asistencia.objects.create(
                        fecha_asistencia=fecha,
                        grupo=grupo
                    )
                    asistencia_estudiante= Asistencia_estudiante.objects.bulk_create([Asistencia_estudiante(asistencia=asistencia,estudiante=estudiante) for estudiante in grupo.estudiantes_grupo.filter(inscripcion__estado=True)])
                    return redirect('tomar_asistencia',asistencia=asistencia.id_asistencia)
                else:
                    return render(request, 'informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos})
            
            else:
                return render(request, 'informacion_curso.html', {'grupo': grupo,'profesor': profesor, 'asistencias': datos})
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
                    return render(request, 'listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'mensaje_actualizacion': f'Estudiantes actualizados: {cantidad[0]} estudiantes nuevos, {cantidad[1]} estudiantes eliminados'})
            else:
                estudiantes_activos = grupo.estudiantes_grupo.filter(inscripcion__estado=True).order_by('apellidos_estudiante')
                estudiantes_inactivos = grupo.estudiantes_grupo.filter(inscripcion__estado=False).order_by('apellidos_estudiante')
                return render(request, 'listar_estudiantes_curso.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos})

        except Exception as e:
            print(e)
            return redirect('informacion_curso',grupo=grupo.id_grupo)
    else:
        return redirect('index')

@login_required
def tomar_asistencia(request,asistencia):
    if  'profesor_id' in request.session:
        profesor = Profesores.objects.get(id=request.session['profesor_id'])
        asistencia = Asistencia.objects.get(id_asistencia=asistencia)
        grupo = asistencia.grupo
        estudiantes_activos = grupo.estudiantes_grupo.filter(asistencia_estudiante__registro_Asistencia=True).order_by('apellidos_estudiante')
        estudiantes_inactivos = grupo.estudiantes_grupo.filter(asistencia_estudiante__registro_Asistencia=False).order_by('apellidos_estudiante')
        fecha= asistencia.fecha_asistencia
        print(estudiantes_activos)
        print(estudiantes_inactivos)
        if request.method == 'POST':
            pass
        else:
            return render(request, 'tomar_asistencia.html', {'grupo': grupo,'profesor': profesor, 'estudiantes_activos': estudiantes_activos,'estudiantes_inactivos':estudiantes_inactivos, 'fecha': fecha})
    else:
        return redirect('index')
    return render(request, 'tomar_asistencia.html')

@login_required
def perfil_profesor(request):
    # Crear gráfico

    fig = go.Figure(data=go.Bar(y=[0.98, 0.7, 0.8,0.9], x=['Curso A', 'Curso B', 'Curso C','Curso D']))
    colores=['#9ddea6']*len(fig.data[0].x)
    for i in range(0,len(colores),2):
        colores[i]='#67b072'
    fig.update_traces(marker_color=colores)
    fig.update_layout(
        title="Porcentaje de Asistencia para el semestre 2024-1",
        xaxis_title="Curso",
        yaxis_title="Porcentaje",
        yaxis_tickformat="%",
        yaxis=dict(tickformat=".0%")
    )   
    # Convertir a HTML
    graph = opy.plot(fig, auto_open=False, output_type='div')
    return render(request, 'perfil_profesor.html', {'graph': graph})
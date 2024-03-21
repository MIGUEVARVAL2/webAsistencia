from django.contrib.auth import logout
from .models import UserDevice
from datetime import datetime, timedelta

#Esta función se encarga de extraer la ip del cliente para limitar el acceso a más cuentas

class DeviceCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Eliminar registros antiguos
        self.eliminar_registros_antiguos()
        #En caso de que el usuario esté autenticado y la sesión sea por parte del estudiante, se guarda la ip y la fecha de acceso
        if request.user.is_authenticated and 'estudiante_id' in request.session:
            #Para este caso obtuve 3 ip diferentes, por lo que se obtiene la ip del cliente(?)
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            print("ip2",request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')))
            #Se guarda la ip y la fecha de acceso
            user_device = UserDevice.objects.filter(user=request.user, ip_address=ip_address).first()
            #En caso de que la ip y el usuario sean iguales a la encontrada en el modelo se le permite el acceso 
            #De lo contrario significa que está intentando acceder a otra cuenta, entonces se le cierra la sesión
            if not user_device:
                logout(request) 
            print("user_device -1 ",user_device.fecha,user_device.ip_address,user_device.user)
        response = self.get_response(request)
        return response
    
    #Valida los registros que llevan más de 5 minutos en la base de datos y los elimina
    def eliminar_registros_antiguos(self):
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        # Calcular el tiempo límite 
        fecha_limite = fecha_actual - timedelta(minutes=5)
        # Eliminar registros anteriores 
        registros_eliminados = UserDevice.objects.filter(fecha__lt=fecha_limite)
        print("Eliminando registros antiguos:")
        for registro in registros_eliminados:
            print("Eliminado",registro.fecha, registro.ip_address, registro.user)

        registros_eliminados.delete()
        # Imprimir todos los registros del modelo UserDevice
        registros = UserDevice.objects.all()
        for registro in registros:
            print("En la base de datos",registro.fecha, registro.ip_address, registro.user)
        
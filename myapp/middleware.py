from django.contrib.auth import logout
from .models import UserDevice
from datetime import datetime, timedelta

class DeviceCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.eliminar_registros_antiguos()
        if request.user.is_authenticated and 'estudiante_id' in request.session:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '')).split(',')[0].strip()
            print("ip2",ip_address)
            user_device = UserDevice.objects.filter(user=request.user, ip_address=ip_address).first()
            print("user_device",user_device.fecha,user_device.ip_address,user_device.user)
            if not user_device:
                logout(request)  # cierra la sesión del usuario si la dirección IP no coincide

        response = self.get_response(request)
        return response
    
    def eliminar_registros_antiguos(self):
        # Obtener la fecha actual
        fecha_actual = datetime.now().date()
        # Calcular la fecha límite (ayer)
        fecha_limite = fecha_actual - timedelta(minutes=5)
        # Eliminar registros anteriores al día actual
        UserDevice.objects.filter(fecha__lt=fecha_limite).delete()
        print("Eliminando registros antiguos")
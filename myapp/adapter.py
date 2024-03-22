# adapter.py

from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from .models import Estudiantes

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        # No permitir registro de nuevos usuarios
        return False

    def populate_user(self, request, sociallogin, data):
        User = get_user_model()
        try:
            user = User.objects.filter(email=data['email']).first()
            print(data['email'],user.email,user.id)
            if user is None:
                raise ValidationError('No existe una cuenta con este correo electrónico.')
            else:
                estudiante= Estudiantes.objects.get(user=user)
                request.session['estudiante_id'] = estudiante.id
        except User.DoesNotExist:
            raise ValidationError('No existe una cuenta con este correo electrónico.')
        return user
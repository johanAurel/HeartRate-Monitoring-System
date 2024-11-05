from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

class SQLiteAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            # Authenticate using Django's built-in ORM
            user = User.objects.filter(username=username).first()
            
            if user is not None and user.check_password(password):
                return user

            return None
        
        except Exception as e:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

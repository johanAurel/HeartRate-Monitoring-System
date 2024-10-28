# heart_rate_app/auth_backend.py

import mysql.connector
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend

class MySQLAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            connection = mysql.connector.connect(
                host='localhost',
                user=username,
                password=password,
                database='mysql'  # Default database for MySQL users
            )
            if connection.is_connected():
                user, created = User.objects.get_or_create(username=username)
                if created:
                    user.set_unusable_password()  # Set unusable password for the Django user
                return user

        except mysql.connector.Error as err:
            return None
        
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

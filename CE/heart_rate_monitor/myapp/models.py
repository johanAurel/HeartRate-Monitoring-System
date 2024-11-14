
from django.contrib.auth.models import AbstractUser
from django.db import models

class MyCustomUser(AbstractUser):
    # Custom fields if needed
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    class Meta:
        db_table = 'myapp_mycustomuser'


class Device(models.Model):
    STATUS_CHOICES = [
        ('on', 'On'),
        ('off', 'Off'),
    ]

    id = models.AutoField(primary_key=True)  # Explicit serial primary key
    user = models.ForeignKey(MyCustomUser, on_delete=models.CASCADE, related_name='devices')
    name = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100, unique=True)  # Unique identifier
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='off')  # New field

    def __str__(self):
        return f"{self.name} - {self.status}"

class Heartbeat(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='heartbeats')
    timestamp = models.DateTimeField(auto_now_add=True)
    rate = models.IntegerField()

    def __str__(self):
        return f"{self.device.name} - {self.timestamp}"


class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='alerts')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.device.name} at {self.timestamp}"

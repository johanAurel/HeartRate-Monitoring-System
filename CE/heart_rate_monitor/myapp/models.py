from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser
import paho.mqtt.client as mqtt



class CustomUser(AbstractUser):
   email = models.EmailField(unique = True)


   def __call__(self, *args, **kwds):
       return self.email.email
 
class Device(models.Model):
    machine_states = [('ON', 'ON'), ('OFF', 'OFF')]
    
    # Reference to the User model
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    device_name = models.CharField(max_length=128)   
    status = models.CharField(max_length=3, choices=machine_states, default='OFF')

    def __str__(self):
        return f"{self.device_name} - {self.status} ({self.user.username})"
    
class Heartbeat(models.Model):

    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    last_heartbeat = models.DateTimeField(null=True)
    heartbeat_rate = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.last_heartbeat = timezone.now()
        super().save(*args, **kwargs)    
    def __str__(self):
        return f"{self.device.device_name} - {self.heart_rate} bpm at {self.last_heartbeat}"
    

class Alert(models.Model):
   
   device = models.ForeignKey(Device, on_delete=models.CASCADE)
   heartbeat = models.ForeignKey(Heartbeat, on_delete=models.CASCADE)
   alert_message = models.CharField(max_length=255)
   
   def clean(self):
         
         if self.heartbeat.heartbeat_rate <= 100:
            raise ValidationError('Heartbeat rate must be greater than 100 BPM.')

   def save(self, *args, **kwargs):
        # Set heartbeat rate and last heartbeat based on the related heartbeat instance
        if self.heartbeat:
            self.heartbeat_rate = self.heartbeat.heartbeat_rate
            self.last_heartbeat = self.heartbeat.last_heartbeat
            self.device = self.heartbeat.device  # Set the device for the alert
        # Validate before saving
        self.clean()
        super().save(*args, **kwargs)
   
   def __str__(self):
        return f"Alert for {self.device.device_name} - {self.alert_message} at {self.heartbeat.last_heartbeat}"

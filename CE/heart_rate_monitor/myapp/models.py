from django.db import models
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db.models import F


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
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    last_heartbeat = models.DateTimeField(null=True)
    heartbeat_rate = models.IntegerField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.last_heartbeat = timezone.now()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.device.device_name} - {self.heartbeat_rate} bpm at {self.last_heartbeat}"

    @staticmethod
    def check_and_create_alert(device):
        """
        Checks the most recent heartbeat of a device and creates an alert if needed.
        """
        heartbeat = Heartbeat.objects.filter(device=device).last()
        if not heartbeat:
            return None  # No heartbeat data for this device

        if heartbeat.heartbeat_rate > 100:
            alert_message = f"ALERT: High Heartbeat Rate - {heartbeat.heartbeat_rate} BPM!"
            alert = Alert.objects.create(
                device=device,
                heartbeat=heartbeat,
                alert_message=alert_message
            )
            return alert
        elif heartbeat.heartbeat_rate < 80:
            alert_message = f"ALERT: Low Heartbeat Rate - {heartbeat.heartbeat_rate} BPM!"
            alert = Alert.objects.create(
                device=device,
                heartbeat=heartbeat,
                alert_message=alert_message
            )
            return alert
        return None  # No alert needed

class Alert(models.Model):
    device = models.ForeignKey('Device', on_delete=models.CASCADE)
    heartbeat = models.ForeignKey('Heartbeat', on_delete=models.CASCADE)
    alert_message = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Check if the heartbeat rate is valid before saving
        if self.heartbeat.heartbeat_rate <= 100:
            raise ValidationError("Heartbeat rate must be greater than 100 BPM.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Alert for {self.device.device_name} - {self.alert_message} at {self.heartbeat.last_heartbeat}"

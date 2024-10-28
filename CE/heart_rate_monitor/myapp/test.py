from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from myapp.models import Device

class DeviceListViewTest(TestCase):
    def setUp(self):
        # Create two users and two devices
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.device1 = Device.objects.create(user=self.user1, name='Device 1', status='ON')
        self.device2 = Device.objects.create(user=self.user2, name='Device 2', status='OFF')

    def test_user_can_only_access_own_devices(self):
        # Log in as user1
        self.client.login(username='user1', password='password123')
        
        # Access the device list view
        response = self.client.get(reverse('device_list'))
        
        # Ensure that user1 only sees their own device
        self.assertContains(response, 'Device 1')
        self.assertNotContains(response, 'Device 2')
    
    def test_superuser_can_access_all_devices(self):
        # Create a superuser
        superuser = User.objects.create_superuser(username='admin', password='adminpassword')
        
        # Log in as the superuser
        self.client.login(username='admin', password='adminpassword')
        
        # Access the device list view
        response = self.client.get(reverse('device_list'))
        
        # Ensure the superuser sees all devices
        self.assertContains(response, 'Device 1')
        self.assertContains(response, 'Device 2')

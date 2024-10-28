from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Device

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')  # Add any additional fields you need

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['user', 'device_name', 'machine_state']  # Ensure these fields exist in the Device model
        widgets = {
            'device_name': forms.TextInput(attrs={'placeholder': 'Enter device name'}),  # Update to device_name
            'machine_state': forms.Textarea(attrs={'placeholder': 'Enter machine state'}),  # Update to machine_state
        }
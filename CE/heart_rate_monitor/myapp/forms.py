from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Device

CustomUser = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')  # Add any additional fields as needed
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')

class DeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['user', 'name', 'status']  # Ensure these fields exist in the Device model
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter device name'}),  # Update to device_name
            'status': forms.Textarea(attrs={'placeholder': 'Enter machine state'}),  # Update to status
        }
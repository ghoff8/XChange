from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text= 'We will send a confirmation email to verify your account.')
    #password1 = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email',)
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=24)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'password',)
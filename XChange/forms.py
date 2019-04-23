from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, SetPasswordForm, UserChangeForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text= 'We will send a confirmation email to verify your account.')
    #username = forms.CharField(label=("Password"), widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'email',)
        
class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=24)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('username', 'password',)
        
class SettingsPasswordForm(SetPasswordForm):
    
    class Meta:
        model = User
        fields = ('password1', 'password2')
        help_texts = ""
        
class SettingsEmailForm(UserChangeForm):
    email1 = forms.EmailField(max_length=254)
    email2 = forms.EmailField(max_length=254)
    
    class Meta:
        model = User
        fields =('email1', 'email2')
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import re


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border rounded px-3 py-2 mt-1',
            'placeholder': 'Enter password'
        }),
        min_length=8,
        max_length=128,
        help_text="Password must be at least 8 characters long and contain uppercase, lowercase, and numbers."
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full border rounded px-3 py-2 mt-1',
            'placeholder': 'Confirm password'
        }),
        min_length=8,
        max_length=128
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full border rounded px-3 py-2 mt-1', 'placeholder': 'Enter username'}),
            'email': forms.EmailInput(attrs={'class': 'w-full border rounded px-3 py-2 mt-1', 'placeholder': 'Enter email'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        if not username:
            raise forms.ValidationError("Username is required.")
        
        username = username.strip()
        
        if len(username) < 3:
            raise forms.ValidationError("Username must be at least 3 characters long.")
        
        if len(username) > 150:
            raise forms.ValidationError("Username must be at most 150 characters long.")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise forms.ValidationError("Username can only contain letters, numbers, and underscores.")
        
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("A user with this username already exists.")
        
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if not email:
            raise forms.ValidationError("Email is required.")
        
        email = email.strip().lower()
        
        if len(email) > 254:
            raise forms.ValidationError("Email address is too long.")
        
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError("Please enter a valid email address.")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise forms.ValidationError("Please enter a valid email address.")
        
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if not password:
            raise forms.ValidationError("Password is required.")
        
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        
        if len(password) > 128:
            raise forms.ValidationError("Password must be at most 128 characters long.")
        
        if not re.search(r'[A-Z]', password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r'[a-z]', password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r'[0-9]', password):
            raise forms.ValidationError("Password must contain at least one number.")
        
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match. Please try again.")
        
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500',
            'placeholder': 'Enter your password'
        })
    )

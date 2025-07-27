from django.db import models
from django.contrib.auth.models import AbstractUser

from django import forms
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', default='profiles/default.jpg')

    def __str__(self):
        return self.username

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone', 'profile_picture']


# Create your models here.

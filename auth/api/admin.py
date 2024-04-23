from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class MyUserAdmin(BaseUserAdmin):
    # Qui puoi aggiungere personalizzazioni alla configurazione admin del modello User
    pass

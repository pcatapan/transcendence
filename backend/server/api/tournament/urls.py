from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .controllers.tournament import post

urlpatterns = [
	path('tournament/create', post, name='tournament_create')
]
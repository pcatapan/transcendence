from django.urls import path, include

urlpatterns = [
    path('', include('api.authuser.urls')),
    path('', include('api.tournament.urls')),
]

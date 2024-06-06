from django.urls import path

from .controllers.tournament import post, createNextRound

urlpatterns = [
	path('tournament/create', post, name='tournament_create'),

	path('tournament/next-round/<int:tournament_id>', createNextRound, name='tournament_next_round'),
]
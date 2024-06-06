from django.db import models
from api.authuser.models.custom_user import CustomUser as User

class Tournament(models.Model):
	name = models.CharField(
		max_length=100
	)

	type = models.CharField(
		max_length=100,
		blank=True,
		null=True
	)

	start_date = models.DateField(
		blank=True,
		null=True
	)

	end_date = models.DateField(
		blank=True,
		null=True
	)

	round = models.IntegerField(
		default=0
	)

	winner = models.ForeignKey(
		'Player',
		on_delete=models.CASCADE,
		related_name='winner_tournament',
		blank=True,
		null=True
	)

	tournament_admin = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='tournament_admin',
		blank=True,
		null=True
	)

	joinable = models.BooleanField(
		default=True
	)

	def __str__(self):
		return f"Tournament {self.id} - {self.name}"
	
	@property
	def is_ongoing(self):
		return self.start_date and not self.end_date

	@property
	def is_concluded(self):
		return bool(self.end_date)
	
	def to_json(self):
		return {
			'id': self.id,
			'name': self.name,
			'type': self.type,
			'start_date': self.start_date,
			'end_date': self.end_date,
			'round': self.round,
			'winner': self.winner.name if self.winner else None,
			'tournament_admin': self.tournament_admin.username if self.tournament_admin else None,
			'joinable': self.joinable
		}
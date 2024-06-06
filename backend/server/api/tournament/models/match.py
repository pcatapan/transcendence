from django.db import models

class Match(models.Model):
	player1_score = models.IntegerField(
		default=0
	)

	player2_score = models.IntegerField(
		default=0
	)

	player1 = models.ForeignKey(
		'authuser.CustomUser',
		on_delete=models.CASCADE,
		related_name='player1'
	)

	player2 = models.ForeignKey(
		'authuser.CustomUser',
		on_delete=models.CASCADE,
		related_name='player2',
		null=True
	)
	
	winner = models.ForeignKey(
		'authuser.CustomUser',
		on_delete=models.CASCADE,
		related_name='winner',
		blank=True,
		null=True
	)

	date_played = models.DateTimeField(
		blank=True,
		null=True
	)

	active = models.BooleanField(
		default=False
	)

	def loser(self):
		return self.player1 if self.winner == self.player2 else self.player2
	
	def to_json(self):
		return {
			'player1': self.player1.username,
			'player1_id': self.player1.id,
			'player2': self.player2.username,
			'player2_id': self.player2.id,
			'player1_score': self.player1_score,
			'player2_score': self.player2_score,
			'date_played': self.date_played,
			'active': self.active,
			'loser':  None if self.player1_score == self.player2_score else self.loser().username,
		}

	def __str__(self):
		return f"Match {self.id} - {self.player1} vs {self.player2}"
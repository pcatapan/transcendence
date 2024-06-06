from django.db import models

class LocalMatch(models.Model):
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)
    player1 = models.ForeignKey('Player', related_name='local_player1_matches', on_delete=models.CASCADE)
    player2 = models.ForeignKey('Player', related_name='local_player2_matches', on_delete=models.CASCADE, null=True, blank=True)
    winner = models.ForeignKey('Player', related_name='local_winner_matches', on_delete=models.CASCADE, null=True, blank=True)
    tournament = models.ForeignKey('Tournament', related_name='local_matches', on_delete=models.CASCADE)
    date_played = models.DateTimeField(blank=True, null=True)
    active = models.BooleanField(default=False)
    played = models.BooleanField(default=False)
    round = models.IntegerField(default=0)

    def loser(self):
        return self.player1 if self.winner == self.player2 else self.player2

    def to_json(self):
        return {
            'id': self.id,
            'player1': self.player1.name,
            'player2': self.player2.name if self.player2 else None,
            'player1_score': self.player1_score,
            'player2_score': self.player2_score,
            'date_played': self.date_played,
            'active': self.active,
            'loser': None if self.player1_score == self.player2_score else self.loser().name,
            'winner': self.winner.name if self.winner else None,
        }

    def __str__(self):
        player2_name = self.player2.name if self.player2 else None
        return f"Local Match {self.id} - {self.player1.name} vs {player2_name}"
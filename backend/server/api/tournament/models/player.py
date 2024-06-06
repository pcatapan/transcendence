from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    tournament = models.ForeignKey('Tournament', related_name='players', on_delete=models.CASCADE)

    def __str__(self):
        return f"Player {self.name} in Tournament {self.tournament.name}"
from django.db import models

class Friendship(models.Model):
	user = models.OneToOneField(
		'authuser.CustomUser',
		on_delete=models.CASCADE,
		related_name='user_friends'
	)

	friends = models.ManyToManyField(
		'authuser.CustomUser',
		related_name='friends',
		blank=True
	)

	def to_json(self):
		return {
			'user': self.user.to_json(),
			'friends': [friend.to_json() for friend in self.friends.all()],
		}

	def __str__(self):
		return f'{self.user.id} {self.user.username}\'s friends'
    
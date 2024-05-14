from django.db import models
from .custom_user import CustomUser

class Friendship(models.Model):
	user = models.OneToOneField(
		CustomUser,
		on_delete=models.CASCADE,
		related_name='user_friends'
	)

	friends = models.ManyToManyField(
		CustomUser,
		related_name='friends',
		blank=True
	)

	blocked_users = models.ManyToManyField(
		CustomUser,
		related_name='blocked_users',
		blank=True
	)

	def to_json(self):
		return {
			'user': self.user.to_json(),
			'friends': [friend.to_json() for friend in self.friends.all()],
			'blocked_users': [blocked_user.to_json() for blocked_user in self.blocked_users.all()]
		}

	def __str__(self):
		return f'{self.user.id} {self.user.username}\'s friends'
    
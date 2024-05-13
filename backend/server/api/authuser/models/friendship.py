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

    def __str__(self):
        return f'{self.user.id} {self.user.username}\'s friends'
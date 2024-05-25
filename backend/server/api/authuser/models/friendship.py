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

	blocked_users = models.ManyToManyField(
		'authuser.CustomUser',
		related_name='blocked_users',
		blank=True
	)

	def to_json(self):
		return {
			'user': self.user.to_json(),
			'friends': [friend.to_json() for friend in self.friends.all()],
			'blocked_users': [blocked_user.to_json() for blocked_user in self.blocked_users.all()]
		}
	
	# Ritorna tutti gli amici e gli utenti bloccati in un unico array
	def get_all(self):
		users_json = [{'id': index + 1, **user.to_json(), 'type': 'friend'} for index, user in enumerate(self.friends.all())]
		blocked_users_json = [{'id': index + 1 + len(users_json), **user.to_json(), 'type': 'blocked'} for index, user in enumerate(self.blocked_users.all())]
		
		return users_json + blocked_users_json


	def __str__(self):
		return f'{self.user.id} {self.user.username}\'s friends'
    
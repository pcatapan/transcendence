import os
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db.models import JSONField, Q, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .friendship import Friendship

default_avatar = '/media/avatars/default.png'

class CustomUser(AbstractUser):
	email = models.EmailField(
		unique=True,
		null=False,
		blank=False
	)

	fullname = models.CharField(
		max_length=100,
		null=False,
		blank=False
	)

	avatar = models.ImageField(
		upload_to='avatars/',
		null=True,
		blank=True
	)

	login = models.CharField(
		max_length=100,
		null=True,
		blank=True,
		default=None
	)

	is_2fa_enabled = models.BooleanField(default=False)

	is_2fa_setup_complete = models.BooleanField(
		default=False
	)

	secret_key = models.CharField(
		max_length=255,
		null=True,
		blank=True
	)

	groups = models.ManyToManyField(
		Group,
		verbose_name=_('groups'),
		blank=True,
		help_text=_('The groups this user belongs to.'),
		related_name='customuser_set',
		related_query_name='user',
	)

	user_permissions = models.ManyToManyField(
		Permission,
		verbose_name=_('user permissions'),
		blank=True,
		help_text=_('Specific permissions for this user.'),
		related_name='customuser_set',
		related_query_name='user',
	)

	ELO = models.IntegerField(
		default=0
	)

	list_of_sent_invites = JSONField(
		default=list,
		blank=True
	)

	list_of_received_invites = JSONField(
		default=list,
		blank=True
	)

	def update_avatar(self, new_avatar):
		if self.avatar:
			self.avatar.delete()

		self.avatar = new_avatar
		self.save()


	def enable_2fa(self, secret_key):
		self.is_2fa_enabled = True
		self.secret_key = secret_key
		self.save()

	def disable_2fa(self):
		self.is_2fa_enabled = False
		self.secret_key = None
		self.is_2fa_setup_complete = False
		self.save()

	def add_received_invites(self, invite_id, invite_type):
		self.list_of_received_invites.append({
			'invite_id': invite_id,
			'invite_type': invite_type,
			'time': timezone.now().isoformat(),
		})

		self.save()

	def remove_received_invites(self, invite_id, invite_type):
		self.list_of_received_invites = [
			invite for invite in self.list_of_received_invites
			if not (invite['invite_id'] == invite_id and invite['invite_type'] == invite_type)
		]

		self.save()

	def add_sent_invites(self, invite_id, invite_type):
		self.list_of_sent_invites.append({
			'invite_id': invite_id,
			'invite_type': invite_type,
			'time': timezone.now().isoformat(),
        })
		
		self.save()

	def remove_sent_invites(self, invite_id, invite_type):
		self.list_of_sent_invites = [
			invite for invite in self.list_of_sent_invites
			if not (invite['invite_id'] == invite_id and invite['invite_type'] == invite_type)
		]

		self.save()

	# Sovrascrivere il metodo save
	def save(self, *args, **kwargs):
		# Aggiungere un avatar di default se non è stato fornito
		if not self.avatar:
			self.avatar = 'avatars/default.png'

		super(CustomUser, self).save(*args, **kwargs)

	def get_sent_invites(self):
		return self.list_of_sent_invites

	def get_received_invites(self):
		return self.list_of_received_invites

	def __str__(self):
		return f'{self.id} {self.username}'

	def to_json(self):
		return {
			'id'        : self.id,
			'username'  : self.username,
			'email'     : self.email,
			'avatar'    : self.avatar.url if self.avatar else default_avatar,
		}
	
	def to_json_full(self):

		frindship = Friendship.objects.get(user=self)

		return {
			'id'        	: self.id,
			'username'  	: self.username,
			'email'     	: self.email,
			'fullname'  	: self.fullname,
			'avatar'    	: self.avatar.url if self.avatar else default_avatar,
			'elo'       	: self.ELO,
			'2FA'			: self.is_2fa_enabled and self.is_2fa_setup_complete,
			'friends'   	: frindship.get_all(),
			'match_history' : self.get_match_history(),
			'user_stats'	: self.user_stats()
		}
	
	def get_match_history(self):
		from api.tournament.models.match import Match
		matches = Match.objects.filter(Q(player1=self) | Q(player2=self)).select_related('player1', 'player2')

		if not matches:
			return []

		return [match.to_json() for match in matches]
	
	def user_stats(self):
		from api.tournament.models.match import Match
		matches = Match.objects.filter(Q(player1=self) | Q(player2=self))

		if not matches:
			return {
				'total_matches': 0,
				'wins': 0,
				'losses': 0,
				'tie': 0,
				'goal_scored': 0,
				'goal_conceded': 0,
				'win_rate': 0,
				'loss_rate': 0,
				'tie_rate': 0
			}

		total_matches = matches.count()
		wins = matches.filter(winner=self, active=False).exclude(player1_score=F('player2_score')).count()
		tie = matches.filter(player1_score=F('player2_score')).count()
		losses = total_matches - wins - tie
		goal_scored = sum([match.player1_score for match in matches if match.player1 == self]) + sum([match.player2_score for match in matches if match.player2 == self])
		goal_conceded = sum([match.player2_score for match in matches if match.player1 == self]) + sum([match.player1_score for match in matches if match.player2 == self])

		win_rate = (wins / total_matches) * 100
		loss_rate = (losses / total_matches) * 100
		tie_rate = (tie / total_matches) * 100

		return {
			'total_matches': total_matches,
			'wins': wins,
			'losses': losses,
			'tie': tie,
			'goal_scored': goal_scored,
			'goal_conceded': goal_conceded,
			'win_rate': win_rate,
			'loss_rate': loss_rate,
			'tie_rate': tie_rate
		}
 
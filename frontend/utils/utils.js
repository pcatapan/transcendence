import { userService } from '../../services/user-service.js';
import { showSnackbar } from './snackbar.js';

export function generateRandomAvatar() {
  const randomNum = Math.floor(Math.random() * 100);

  return `https://www.gravatar.com/avatar/${randomNum}?d=identicon`;
}

export async function defineOpponentTournament() {
	let res = await userService.userProfile(localStorage.getItem('user'));
	if (res.status !== 200) {
		showSnackbar(res.body.message, 'error');
		return;
	}

	let user = res.body.data;
	let match = JSON.parse(localStorage.getItem('currentMatch'))

	if (user.username === match.player1) {
		window.game.opponent = {
			name: match.player2,
			avatar: generateRandomAvatar()
		}

		window.game.player1 = {
			name: user.username,
			avatar: user.avatar
		}
	} else if (user.username === match.player2) {
		window.game.player1 = {
			name: match.player1,
			avatar: generateRandomAvatar()
		}

		window.game.opponent = {
			name: user.username,
			avatar: user.avatar
		}
	} else {
		// Partita tra due utenti non autenticati
		window.game.opponent = {
			name:  match.player2,
			avatar: generateRandomAvatar()
		}

		window.game.player1 = {
			name : match.player1,
			avatar : generateRandomAvatar()
		}
	}
}
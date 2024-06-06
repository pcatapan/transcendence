import { userService } from '../../services/user-service.js';
import { showSnackbar } from './snackbar.js';

export function generateRandomAvatar() {
  const randomNum = Math.floor(Math.random() * 100);

  return `https://www.gravatar.com/avatar/${randomNum}?d=identicon`;
}

export async function defineOpponentTournament() {
	console.log('caricio le info del mio user')
	let res = await userService.userProfile(localStorage.getItem('user'));
	console.log(res)
	if (res.status !== 200) {
		console.log(res)
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
		window.game.opponent = {
			name: match.player1,
			avatar: generateRandomAvatar()
		}

		window.game.player1 = {
			name: user.username,
			avatar: user.avatar
		}
	} else {
		// Partita tra due utenti non autenticati
		window.game.opponent = {
			name:  match.player1,
			avatar: generateRandomAvatar()
		}

		window.game.player1 = {
			name : match.player2,
			avatar : generateRandomAvatar()
		}
	}
}
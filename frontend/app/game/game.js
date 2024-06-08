import { initializeGameSocket, sendMessage } from "../../websocket/Game.js";
import { commands } from "../../websocket/command.js";
import { APP_ENV, gameMode } from "../../enviroments.js";
import { showSnackbar } from "../../utils/snackbar.js";
import { userService } from "../../services/user-service.js";

const Game = () => {
    console.log("Game component loaded");

    if (window.game['mode'] !== 'online' && window.game['mode'] !== 'tournament') {
        document.getElementById('button-home').style.display = 'flex';
    } else {
        document.getElementById('button-home').style.display = 'none';
    }
    
    initializeGameSocket(window.game.match_id);

    if (window.game.mode !== gameMode.tournament) {
        let data = {
            'match': window.game.match_id
        }
        sendMessage(window.ws, commands.confirm_match, data);

        animationFoundOpponent();
    } else {
        showInfoMatch();
    }

    // Gestisci il rilascio dei tasti
	document.addEventListener('keyup', (event) => {
        if (window.game.isActive === false)
            return;

		if (event.key === 'ArrowUp') {
			sendMessageKeyboard('up', 'on_release');
		} else if (event.key === 'ArrowDown') {
			sendMessageKeyboard('down', 'on_release');
		}

        if (window.game.mode !== gameMode.offline && window.game.mode !== gameMode.tournament) {
            return;
        }

        if (event.key === 'w') {
            sendMessageKeyboard('w', 'on_release');
        }
        else if (event.key === 's') {
            sendMessageKeyboard('s', 'on_release');
        }
	});

    // Gestisci la pressione dei tasti
	document.addEventListener('keydown', (event) => {
        if (window.game.isActive === false)
            return;

		if (event.key === 'ArrowUp') {
			sendMessageKeyboard('up', 'on_press');
		} else if (event.key === 'ArrowDown') {
			sendMessageKeyboard('down', 'on_press');
		}

        if (window.game.mode !== gameMode.offline && window.game.mode !== gameMode.tournament) {
            return;
        }

        if (event.key === 'w') {
            sendMessageKeyboard('w', 'on_press');
        }
        else if (event.key === 's') {
            sendMessageKeyboard('s', 'on_press');
        }
	});
};

function animationFoundOpponent() {
    let opponent = window.game.opponent;

    let user
    userService.userProfile(localStorage.getItem('user')).then((response) => {
        if (response.status === 200) {
            user = response.body.data;
        }else {
            showSnackbar(`${response.body.message}`, 'error');
        }
    })

    document.getElementById('opponent-avatar').src = opponent['avatar'];
    document.getElementById('opponent-name').textContent = opponent['name'];

    // Countdown
    let countdown = 5;
    if (APP_ENV === 'development' && false) {
        countdown = 1;
    }

    let countdownElement = document.getElementById('countdown');
    countdownElement.textContent = countdown;

    let countdownInterval = setInterval(() => {
        countdown--;
        countdownElement.textContent = countdown;

        if (countdown === 0) {
            clearInterval(countdownInterval);
            countdownElement.textContent = 'GO!';

            setTimeout(() => {
                countdownElement.style.opacity = 0;
                preparingMatch({
                    name: user.username,
                    avatar: user.avatar
                }, opponent);

            }, 500);
        }
    }, 1000);
}

function sendMessageKeyboard(key, status) {
    const message = {
        command: commands.keyboard,
        key: key,
        key_status: status
    };
    window.ws_game.send(JSON.stringify(message));
}

function showInfoMatch() {
    // Aggiungo attributo hidden
    document.getElementById('opponent-info').classList.add('d-none');

    document.getElementById('match-info').removeAttribute('hidden');

    document.getElementById('player1').textContent = window.game.player1.name;
    document.getElementById('player1-avatar-info').src = window.game.player1.avatar;

    document.getElementById('player2').textContent = window.game.opponent.name;
    document.getElementById('player2-avatar-info').src = window.game.opponent.avatar;

    document.getElementById('button-start-game').onclick = () => {
        document.getElementById('match-info').setAttribute('hidden', true);
        
        preparingMatch(window.game.player1, window.game.opponent);

        window.game.isActive = true;
        sendMessage(window.ws_game, commands.start_ball);
    }
}

function preparingMatch(player1, player2) {
    // opacity 0
    document.getElementById('opponent-info').style.opacity = 0;

    // Rimuovo attribbuto hidden
    document.getElementById('game-container').removeAttribute('hidden');
    
    // Aggiungo attributo hidden
    document.getElementById('opponent-info').setAttribute('hidden', true);

    // rimuovo d-flex
    document.getElementById('opponent-info').classList.remove('d-flex');

    document.getElementById('player2-avatar').src = player2['avatar'];
    document.getElementById('player2-name').textContent = player2['name'];

    document.getElementById('player1-avatar').src = player1['avatar'];
    document.getElementById('player1-name').textContent = player1['name'];
}

// Al caricamento di pagina
document.addEventListener('DOMContentLoaded', function() {
   window.navigateTo("/");
});

export default Game;

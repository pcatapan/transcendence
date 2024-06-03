import { initializeGameSocket, sendMessage } from "../../websocket/Game.js";
import { commands } from "../../websocket/command.js";
import { APP_ENV } from "../../enviroments.js";

const Game = () => {
    console.log("Game component loaded");
    
    initializeGameSocket(window.game.match_id);

    let data = {
        'match': window.game.match_id
    }
    sendMessage(window.ws, commands.confirm_match, data);

    animationFoundOpponent();

    // Gestisci il rilascio dei tasti
	document.addEventListener('keyup', (event) => {
        console.log('Game isActive:', window.game.isActive, "keyup event: ", event.key);
        if (window.game.isActive === false)
            return;

		if (event.key === 'ArrowUp') {
			sendMessageKeyboard('up', 'on_release');
		} else if (event.key === 'ArrowDown') {
			sendMessageKeyboard('down', 'on_release');
		}
	});

    // Gestisci la pressione dei tasti
	document.addEventListener('keydown', (event) => {
        console.log('Game isActive:', window.game.isActive, "keydown event: ", event.key);
        if (window.game.isActive === false)
            return;

		if (event.key === 'ArrowUp') {
			sendMessageKeyboard('up', 'on_press');
		} else if (event.key === 'ArrowDown') {
			sendMessageKeyboard('down', 'on_press');
		}
	});
};

function animationFoundOpponent() {
    let opponent = window.game.opponent;

    console.log('Found opponent:', opponent);

    document.getElementById('opponent-avatar').src = opponent.avatar;
    document.getElementById('opponent-name').textContent = opponent.username;

    // Countdown
    let countdown = 5;
    if (APP_ENV === 'development') {
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
                // opacity 0
                document.getElementById('opponent-info').style.opacity = 0;
                countdownElement.style.opacity = 0;

                // Rimuovo attribbuto hidden
                document.getElementById('game-container').removeAttribute('hidden');
                
                // Aggiungo attributo hidden
                document.getElementById('opponent-info').setAttribute('hidden', true);
                // rimuovo d-flex
                document.getElementById('opponent-info').classList.remove('d-flex');

                startGame();
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

function startGame() {
    console.log('Game started');
}

export default Game;

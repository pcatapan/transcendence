import { initializeGameSocket, sendMessage } from "../../websocket/Game.js";
import { commands } from "../../websocket/command.js";
import { APP_ENV } from "../../enviroments.js";


//// Creazione della connessione WebSocket
//const socket = new WebSocket('ws://localhost/ws/pong/12'); // Sostituisci con l'URL corretto

//// Funzione per inviare l'input della tastiera al WebSocket
//function sendKeyboardInput(key, status) {
//    const message = {
//        command: 'keyboard',
//        key: key,
//        key_status: status
//    };
//    socket.send(JSON.stringify(message));
//}

//// Gestione della connessione aperta
//socket.onopen = function(event) {
//    console.log('WebSocket connection opened');
//};

//// Gestione dei messaggi ricevuti dal server
//socket.onmessage = function(event) {
//    console.log('Message from server', event.data);
//};

//// Gestione degli errori
//socket.onerror = function(error) {
//    console.error('WebSocket Error', error);
//};

//// Gestione della connessione chiusa
//socket.onclose = function(event) {
//    console.log('WebSocket connection closed', event);
//};

//// Aggiungi gli event listener per gli input della tastiera
//document.addEventListener('keydown', function(event) {
//    sendKeyboardInput(event.key, 'on_press');
//});

//document.addEventListener('keyup', function(event) {
//    sendKeyboardInput(event.key, 'on_release');
//});

const Game = () => {
    console.log("Game component loaded");
    
    initializeGameSocket(window.game.match_id);

    setTimeout(() => {
        console.log('Aspetto per essere sicuro che venga inizializzata la connessione WebSocket');
    }, 1000);

    sendMessage(window.ws_game, commands.confirm_match);

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
    document.getElementById('opponent-name').textContent = opponent.name;

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

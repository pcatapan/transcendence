import { initializeWebSocket, sendMessage } from '../../websocket/Lobby.js';
import { commands } from '../../websocket/command.js';
import { APP_ENV } from '../../enviroments.js';
import {showSnackbar} from '../../utils/snackbar.js';

const waitingMessages = [
	"Sharpening the paddles...",
	"Drawing the arena...",
	"Summoning the players...",
	"Setting up the net...",
	"Warming up the ball...",
	"Adjusting the scoreboards...",
	"Finalizing game settings...",
	"Preparing an epic match..."
];

const WaitingRoom = async () => {
    console.log("WaitingRoom component loaded");

	function showRandomWaitingText() {
		const randomWaitingText = document.getElementById('random-waiting-text');

		if (!randomWaitingText) {
			clearInterval(intervalId);
			return;
		}

        const randomIndex = Math.floor(Math.random() * waitingMessages.length);
        randomWaitingText.textContent = waitingMessages[randomIndex];
    }
	const intervalId = setInterval(showRandomWaitingText, 3000);

	await initializeWebSocket();

	// Define mode of play
	defineModeOfPlay()
	
	// LEAVE QUEUE
	document.getElementById('button-leave-queue').addEventListener('click', async () => {

		if (window.game.mode === 'ia_opponent') {
			window.ws_game.close();
			window.navigateTo('/home');
			return;
		}

		let data = {
			'queue': 'global'
		}
		sendMessage(window.ws, commands.leave_queue, data);
	});
};

function defineModeOfPlay() {
	switch (window.game.mode) {
		case 'online':
			joinGlobalQueue();
			break;
		case 'ia_opponent':
			startIAOpponentGame();
			break;
		case 'offline':
			startLocalGame();
			break;
		default:
			showSnackbar('Unknown game mode', 'error');
			window.navigateTo('/home');

			console.log('Unknown game mode:', window.game.mode);
			break;
	}
}

function joinGlobalQueue() {
	let data = {
		'queue': 'global'
	}

	sendMessage(window.ws, commands.join_queue, data);
}

function startIAOpponentGame() {
	sendMessage(window.ws, commands.ia_opponent);
}

function startLocalGame() {
	sendMessage(window.ws, commands.local_opponent);
}

export default WaitingRoom;
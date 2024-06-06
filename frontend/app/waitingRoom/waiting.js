import { initializeWebSocket, sendMessage } from '../../websocket/Lobby.js';
import { initializeTournamentGameSocket } from '../../websocket/Game.js';
import { commands } from '../../websocket/command.js';
import { APP_ENV } from '../../enviroments.js';
import { defineOpponentTournament } from '../../utils/utils.js';
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
		case 'tournament':
			startTournamentGame();
			break;
		default:
			showSnackbar('Unknown game mode', 'error');
			window.navigateTo('/');

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

async function startTournamentGame() {

	// In torneo nascondo il bottone di uscita dalla coda
	let quit = document.getElementById('button-leave-queue')
	quit.classList.add('d-none');

	// Cambio il titolo della pagina
	document.getElementById('waiting-room-title').textContent = 'We are preparing the tournament...';

	// Aggiungo pulsante per avviare il torneo
	let startTournamentButton = document.createElement('a');
	startTournamentButton.textContent = 'Start Tournament';
	startTournamentButton.classList.add('btn', 'btn-primary');
	startTournamentButton.onclick = async () => {
		window.navigateTo('/game');
	};
	document.getElementById('waiting-room-container').appendChild(startTournamentButton);

	window.game.tournament = {};
	window.game.endGame = {};

	let tournament = JSON.parse(localStorage.getItem('tournament'));
	window.game.tournament.tournament = tournament;

	let matches = JSON.parse(localStorage.getItem('matches'));
	window.game.tournament.matches = matches;

	window.game.tournament.currentMatch = matches[0];
	let currentMatch = matches[0];
	localStorage.setItem('currentMatch', JSON.stringify(matches[0]));
	
	window.game.tournament.currentMatchIndex = 0;
	localStorage.setItem('currentMatchIndex', 0);

	defineOpponentTournament(currentMatch);

	await initializeTournamentGameSocket(tournament.id, matches[0].id);
}

export default WaitingRoom;
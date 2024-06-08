import { commands } from "./command.js"
import { showSnackbar } from "../utils/snackbar.js"
import { gameMode } from "../enviroments.js";
import { sendMessage } from "./Game.js";
import { generateRandomAvatar } from "../utils/utils.js";

const commandHandlers = {
	[commands.list_of_users]: handler_setUsersList,
	[commands.join_queue]: handler_joinQueue,
	[commands.found_opponent]: handler_foundOpponent,
	[commands.waiting_for_opponent]: handler_WaitingForOpponent,
	[commands.ia_found]: handler_IAOpponentFound,
	[commands.local_found]: handler_LocalOpponentFound,

	[commands.start_ball]: handler_startBall,
	[commands.update_game]: handler_updateGame,
	[commands.finish_match]: handler_finishMatch,
	[commands.confirm_match]: (response) => console.log("Match confirmed:", response.content),
	[commands.send_prv_msg]: () => {}, // Funzione vuota, da definire se necessario,
	[commands.leave_queue]: (response) => console.log("Left queue:", response.content),
	null: (response) => console.log(response.content)
};

function parserRespons(data) {
	let response = JSON.parse(data)

	const handler = commandHandlers[response.command];
	if (handler) {
		handler(response);
	} else {
		console.log('Command not found:', response.command);
	}
}

function handler_setUsersList(res) {
	localStorage.setItem('users_online', JSON.stringify(res.content.users))
}

function handler_joinQueue(res) {
	if (res.content === 'global') {
		console.log('Joined global queue')
		return;
	}

	showSnackbar(res.content, 'info')
}

function handler_foundOpponent(res) {
	// Disabilito il bottone di uscita dalla coda
	let quit = document.getElementById('button-leave-queue')
	quit.classList.add('disabled');
	quit.addEventListener('click', function(event) {
        event.preventDefault(); // Previene la navigazione del link
    });

	// Salvo i dati della partita
	window.game.match_id = res.content.match_id
	window.game.opponent = {
		name : res.content.opponent.username,
		avatar : res.content.opponent.avatar
	}

	setTimeout(() => {
		window.navigateTo('/game');
	}, 1500)
}

function handler_WaitingForOpponent(res) {
	console.log('Waiting for opponent:', res.content)

	document.getElementById('waiting-opponent').classList.remove('d-none')
}

function handler_updateGame(res) {
	document.getElementById('waiting-opponent').classList.add('d-none')
	const { canvas, left_score, right_score, elapsed_time } = res.content;

	// Aggiorna i punteggi
	document.getElementById('player1-score').textContent = left_score;
	document.getElementById('player2-score').textContent = right_score;

	// Aggiorna il canvas
	const gameCanvas = document.getElementById('game-canvas');
	const context = gameCanvas.getContext('2d');

	// Pulisce il canvas
	context.clearRect(0, 0, gameCanvas.width, gameCanvas.height);

	// Disegna la linea centrale
	context.strokeStyle = 'yellow';
	context.lineWidth = 2;
	context.setLineDash([5, 15]);
	context.beginPath();
	context.moveTo(gameCanvas.width / 2, 0);
	context.lineTo(gameCanvas.width / 2, gameCanvas.height);
	context.stroke();
	context.setLineDash([]);

	// Disegna la pallina
	const ball = canvas.ball;
	context.fillStyle = 'white';
	context.shadowBlur = 10;
	context.shadowColor = 'rgba(255, 255, 255, 0.5)';
	context.fillRect(ball.position.x, ball.position.y, ball.size.x, ball.size.y);
	context.shadowBlur = 0;

	// Disegna la palette sinistra
	const leftPaddle = canvas.leftPaddle;
	context.fillStyle = 'blue';
	context.fillRect(leftPaddle.position.x, leftPaddle.position.y, leftPaddle.size.x, leftPaddle.size.y);

	// Disegna la palette destra
	const rightPaddle = canvas.rightPaddle;
	context.fillStyle = 'red';
	context.fillRect(rightPaddle.position.x, rightPaddle.position.y, rightPaddle.size.x, rightPaddle.size.y);

	// Converti elapsed_time in minuti e secondi
	const minutes = Math.floor(elapsed_time / 60);
	const seconds = Math.floor(elapsed_time % 60);
	const formattedTime = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;

	// Disegna il timer
	context.fillStyle = 'white';
	context.font = '20px Arial';
	context.fillText(formattedTime, gameCanvas.width / 2 - context.measureText(formattedTime).width / 2, 30);
}

function handler_startBall(res) {

	if (window.game.mode == gameMode.tournament) {
		// Se è un torneo, non inizio la partita
		return;
	}

	window.game.isActive = true;

	if (!window.ws_game) {
		setTimeout(() => {
			sendMessage(window.ws_game, commands.start_ball);
		}, 1500)
	} else {
		sendMessage(window.ws_game, commands.start_ball);
	}
}

function handler_IAOpponentFound(res) {

	// Salvo i dati della partita
	window.game.match_id = res.content.match_id
	window.game.opponent = {
		name : 'IA',
		avatar : generateRandomAvatar()
	}

	setTimeout(() => {
		window.navigateTo('/game');
	}, 1500)
}

function handler_finishMatch(res) {

	if (window.game.mode === gameMode.tournament) {
		// Salvo i dati di chi ha vinto
		window.game.endGame = {
			winner : res.content.winner_username,
			winner_score : res.content.player1_score > res.content.player2_score ? res.content.player1_score : res.content.player2_score,
			loser : res.content.player1_username === res.content.winner_username ? res.content.player2_username : res.content.player1_username,
			loser_score : res.content.player1_score < res.content.player2_score ? res.content.player1_score : res.content.player2_score,
		}

		setTimeout(() => {
			window.navigateTo('/end-game');
		}, 500)

		return;
	}

	// Svuoto l'oggetto game
	window.game.match_id = null
	window.game.isActive = false
	window.game.opponent = null

	// Salvo i dati di chi ha vinto
	window.game.endGame = {
		winner : res.content.winner_username,
		winner_score : res.content.player1_score > res.content.player2_score ? res.content.player1_score : res.content.player2_score,
		loser : res.content.player1_username === res.content.winner_username ? res.content.player2_username : res.content.player1_username,
		loser_score : res.content.player1_score < res.content.player2_score ? res.content.player1_score : res.content.player2_score,
	}

	setTimeout(() => {
		window.navigateTo('/end-game');
	}, 500)
}

function handler_LocalOpponentFound(res) {
	console.log('Local Opponent found:', res.content)

	// Salvo i dati della partita
	window.game.match_id = res.content.match_id
	window.game.opponent = {
		name : 'Player 2',
		avatar : generateRandomAvatar()
	}

	setTimeout(() => {
		window.navigateTo('/game');
	}, 1500)
}

export { parserRespons }
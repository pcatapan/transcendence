import { commands } from "./command.js"
import { showSnackbar } from "../utils/snackbar.js"
import { sendMessage } from "./Game.js";

const commandHandlers = {
	[commands.list_of_users]: handler_setUsersList,
	[commands.join_queue]: handler_joinQueue,
	[commands.found_opponent]: handler_foundOpponent,
	[commands.waiting_for_opponent]: handler_WaitingForOpponent,
	[commands.ia_found]: handler_IAOpponentFound,

	[commands.start_ball]: handler_startBall,
	[commands.update_game]: handler_updateGame,
	[commands.confirm_match]: () => {}, // Funzione vuota, da definire se necessario
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

	console.log(res.content)

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
	window.game.opponent = res.sender

	setTimeout(() => {
		window.navigateTo('/game');
	}, 1500)
}

function handler_WaitingForOpponent(res) {
	console.log('Waiting for opponent:', res.content)
	
	// Dovrei frizzare la schermata e far apprire alert fisso finche non torna l'opponente o la paritta viene chiusa
}

function handler_updateGame(res) {
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
	console.log('Ball started:', res.content)

	window.game.isActive = true;
	setTimeout(() => {
		sendMessage(window.ws_game, commands.start_ball);
	}, 1500)
}

function handler_IAOpponentFound(res) {
	console.log('IA Opponent found:', res.content)

	// Salvo i dati della partita
	window.game.match_id = res.content.match_id
	window.game.opponent = {
		name : 'IA',
		avatar : 'https://www.gravatar.com/avatar/' + Math.floor(Math.random() * 1000000) + '?d=identicon'
	}

	setTimeout(() => {
		window.navigateTo('/game');
	}, 1500)
}

export { parserRespons }
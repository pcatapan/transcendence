import { APP_ENV } from "../../enviroments.js";

const EndGame = () => {
    console.log("EndGame component loaded");

	let endGameInfo = window.game && window.game.endGame;

	if (APP_ENV === 'development' && false) {
		window.game = {
			endGame : {
				winner: 'Player 1',
				winner_score: 10,
				loser: 'Player 2',
				loser_score: 5
			}
		};
	}

	if (endGameInfo) {
        const endGameContainer = document.getElementById('end-game-info');
        endGameContainer.innerHTML = `
            <div class="card">
                <div class="card-body">
                    <h2 class="card-title text-success">Winner: ${window.game.endGame.winner}</h2>
                    <p class="card-text">Score: ${window.game.endGame.winner_score}</p>
                </div>
            </div>
            <div class="card mt-3">
                <div class="card-body">
                    <h2 class="card-title text-danger">Loser: ${window.game.endGame.loser}</h2>
                    <p class="card-text">Score: ${window.game.endGame.loser_score}</p>
                </div>
            </div>
        `;
    }

    document.getElementById('play-again').addEventListener('click', function(event) {
        window.game.endGame = {};
        window.game.isActive = true;
        window.game.opponent = null;
        window.game.match_id = null;

        window.navigateTo('/waiting-room');
    });
    
};

export default EndGame;
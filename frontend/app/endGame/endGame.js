import { tournamentService } from "../../services/tournament-service.js";
import { defineOpponentTournament } from "../../utils/utils.js";
import { initializeTournamentGameSocket } from "../../websocket/Game.js";
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

    if (window.game.mode === 'tournament') {
        document.getElementById('play-again').classList.add('d-none');
        document.getElementById('button-home').classList.add('d-none');

        document.getElementById('button-next-match').classList.remove('d-none');
    }

    document.getElementById('play-again').addEventListener('click', function(event) {
        window.game.endGame = {};
        window.game.isActive = true;
        window.game.opponent = null;
        window.game.match_id = null;

        window.navigateTo('/waiting-room');
    });

    document.getElementById('button-next-match').addEventListener('click', tournamentNextMatch);
    
};

async function tournamentNextMatch() {
    if (window.game.mode !== 'tournament') {
        return;
    }

    // chiudo il socket
    if (window.ws_game) {
        window.ws_game.close();
        window.ws_game = null;
    }

    const currentMatchIndex = parseInt(localStorage.getItem('currentMatchIndex')) + 1;
    const matches = JSON.parse(localStorage.getItem('matches'));
    const tournament = JSON.parse(localStorage.getItem('tournament'));

    console.log('Next match:', currentMatchIndex);
    console.log('Matches:', matches.length);
    if (currentMatchIndex >= matches.length) {
        let res = await tournamentService.nextRound(tournament.id);

        if (res.status !== 200) {
            console.log(res);
            return;
        }

        let finish = res.body.data.finish;

        if (finish) {
            console.log('Tournament finished');
            updateWinnerInfo(res.body.data.winner);
            return;
        }

        let newMatches = res.body.data.matches;
        localStorage.setItem('matches', JSON.stringify(newMatches));
        localStorage.setItem('tournament', JSON.stringify(res.body.data.tournament));

        setTimeout(() => {
            window.navigateTo('/waiting-room');
        }, 500);

        return;
    }

    window.game.endGame = {};
    window.game.opponent = null;
    window.game.match_id = null;

    let currentMatch = matches[currentMatchIndex];

    localStorage.setItem('currentMatch', JSON.stringify(currentMatch));
    localStorage.setItem('currentMatchIndex', currentMatchIndex);

    defineOpponentTournament(currentMatch);

	await initializeTournamentGameSocket(tournament.id, currentMatch.id);

    setTimeout(() => {
        window.navigateTo('/game');
    }, 500);
}

function updateWinnerInfo(winnerName) {
    const endGameContainer = document.getElementById('end-game-info');
    endGameContainer.innerHTML = `
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-success">Winner: ${winnerName}</h2>
            </div>
        </div>
    `;

    document.getElementById('play-again').classList.add('d-none');
    document.getElementById('button-home').classList.remove('d-none');
    document.getElementById('button-next-match').classList.add('d-none');
}

export default EndGame;
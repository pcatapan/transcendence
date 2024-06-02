import { authService } from '../../services/auth.js';
import { showSnackbar } from '../../utils/snackbar.js';
import { gameMode, APP_ENV } from '../../enviroments.js';
import { initializeWebSocket } from '../../websocket/Lobby.js';


const Home = () => {

    if (APP_ENV === 'development') {
        initializeWebSocket();
    }

    document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 2 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 2 - 1).toFixed(2));
    }); 
    
    document.getElementById('button-signout').addEventListener('click', function(event) {

        if (window.ws) {
            window.ws.close();
            window.ws = null;
        }

        authService.logout().then((response) => {
            if (response.status === 200) {
                localStorage.clear();
                showSnackbar(`${response.body['message']}`, 'success');
                window.navigateTo('/login');
            }
            else{
                showSnackbar(`${response.body['message']}`, 'error');
            }
        })
    });

    document.getElementById('button-game-online').addEventListener('click', function(event) {
        window.game.mode = gameMode.online;

        window.navigateTo('/waiting-room');
    });

    document.getElementById('button-ai-opponent').addEventListener('click', function(event) {
        window.game.mode = gameMode.ia_opponent;

        window.navigateTo('/waiting-room');
    });
};

export default Home;
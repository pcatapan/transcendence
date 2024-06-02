import { webSocketUrl } from '../enviroments.js';
import { authService } from '../services/auth.js';
import { parserRespons } from './handler.js';
import { gameMode } from '../enviroments.js';

async function initializeGameSocket(matchId) {
    if (!window.ws_game) {
        let isAuthorized = await authService.checkAuthorization();
        if (isAuthorized.status === 201) {

            if (window.game.mode === gameMode.online)
                window.ws_game = new WebSocket(`${webSocketUrl}/pong/${matchId}`);

            if (window.game.mode === gameMode.ia_opponent)
                window.ws_game = new WebSocket(`${webSocketUrl}/ai/${matchId}`);
            
			window.ws_game.onmessage = function (event) {
                parserRespons(event.data);
            };

            window.ws_game.onopen = function (event) {
                console.log('WebSocketGame connection opened');
            };

            window.ws_game.onerror = function (error) {
                console.error('WebSocketGame Error', error);
            };

            window.ws_game.onclose = function (event) {
                console.log('WebSocketGame connection closed', event);
            };
        }
    }
    return window.ws_game;
}

async function sendMessage(ws, command, obj = null) {

    if (!ws) {
        console.log('WebSocketGame not initialized');
        return;
    }

    let message = {
        command: command
    };

    if (obj) {
        for (let key in obj) {
            message[key] = obj[key];
        }
    }

    if (ws.readyState === WebSocket.OPEN)
        ws.send(JSON.stringify(message));
    else {
        console.log('WebSocketGame not open');
    }
}

export {sendMessage, initializeGameSocket };
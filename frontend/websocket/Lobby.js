import { webSocketUrl } from '../enviroments.js';
import { authService } from '../services/auth.js';
import { parserRespons } from './handler.js';

async function initializeWebSocket() {
    if (!window.ws) {
        let isAuthorized = await authService.checkAuthorization();
        if (isAuthorized.status === 201) {
            window.ws = new WebSocket(`${webSocketUrl}/lobby`);
            
            window.ws.onmessage = function (event) {
                parserRespons(event.data);
            };

            window.ws.onopen = function (event) {
                console.log('WebSocket connection opened');
            };

            window.ws.onerror = function (error) {
                console.error('WebSocket Error', error);
            };

            window.ws.onclose = function (event) {
                console.log('WebSocket connection closed', event);
            };
        }
    }
    return window.ws;
}

async function initializeWebSocketGame() {
    if (!window.ws_game) {
        let isAuthorized = await authService.checkAuthorization();
        if (isAuthorized.status === 201) {
            window.ws_game = new WebSocket(`${webSocketUrl}/pong/`);
            
            window.ws_game.onmessage = function (event) {
                console.log(JSON.parse(event.data));
            };
        }
    }
    return window.ws_game;
}

async function sendMessage(ws, command, obj = null) {

    if (!ws) {
        console.log('WebSocket not initialized');
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
        console.log('WebSocket not open');
    }
}

export { initializeWebSocket, sendMessage, initializeWebSocketGame };
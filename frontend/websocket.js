import { webSocketUrl } from './enviroments.js';
import { authService } from './services/auth.js';

initializeWebSocket();

async function initializeWebSocket() {
    if (!window.ws) {
        let isAuthorized = await authService.checkAuthorization();
        if (isAuthorized == 201) {
            window.ws = new WebSocket(`${webSocketUrl}/lobby`);
            window.ws.onmessage = function (event) {
                console.log(JSON.parse(event.data));
            };
        }
    }
    return window.ws;
}

export default initializeWebSocket;
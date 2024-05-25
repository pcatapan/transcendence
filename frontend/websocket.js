import { webSocketUrl } from './enviroments.js';
import { authService } from './services/auth.js';

initializeWebSocket();

async function initializeWebSocket() {
	console.log('window', window.ws)
    if (!window.ws) {
        let isAuthorized = await authService.checkAuthorization();
        if (isAuthorized) {
            window.ws = new WebSocket(`${webSocketUrl}/lobby`);

            window.ws.onmessage = function (event) {
                console.log(JSON.parse(event.data));
            };
        }
    }
    return window.ws;
}

export default initializeWebSocket;
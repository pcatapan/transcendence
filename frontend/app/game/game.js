//// Creazione della connessione WebSocket
//const socket = new WebSocket('ws://localhost/ws/pong/12'); // Sostituisci con l'URL corretto

//// Funzione per inviare l'input della tastiera al WebSocket
//function sendKeyboardInput(key, status) {
//    const message = {
//        command: 'keyboard',
//        key: key,
//        key_status: status
//    };
//    socket.send(JSON.stringify(message));
//}

//// Gestione della connessione aperta
//socket.onopen = function(event) {
//    console.log('WebSocket connection opened');
//};

//// Gestione dei messaggi ricevuti dal server
//socket.onmessage = function(event) {
//    console.log('Message from server', event.data);
//};

//// Gestione degli errori
//socket.onerror = function(error) {
//    console.error('WebSocket Error', error);
//};

//// Gestione della connessione chiusa
//socket.onclose = function(event) {
//    console.log('WebSocket connection closed', event);
//};

//// Aggiungi gli event listener per gli input della tastiera
//document.addEventListener('keydown', function(event) {
//    sendKeyboardInput(event.key, 'on_press');
//});

//document.addEventListener('keyup', function(event) {
//    sendKeyboardInput(event.key, 'on_release');
//});

const Game = () => {
    console.log("Game component loaded");

    // Add any JS logic needed for the Sign Out component here
    // e.g., event listeners, DOM manipulations, etc.
};

export default Game;

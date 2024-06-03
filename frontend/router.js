import Home from './app/home/home.js';
import Login from './app/login/login.js';
import PageNotFound from './app/404/404.js';
import SignUp from './app/signUp/signUp.js';
import User from './app/user/user.js';
import Game from './app/game/game.js';
import WaitingRoom from './app/waitingRoom/waiting.js';
import Credits from './app/credits/credits.js';
import EndGame from './app/endGame/endGame.js';

const loadHTML = async (url) => {
    const response = await fetch(url);
    return await response.text();
};

const routes = [
    { path: "/", component: Home, html: '/app/home/home.html', css : '/app/home/home.css'},
    { path: "/login", component: Login, html: '/app/login/login.html', css: '/app/login/login.css'},
    { path: "/sign-up", component: SignUp, html: '/app/signUp/signUp.html', css: '/app/signUp/signUp.css'},
    { path: "/user", component: User, html: '/app/user/user.html', css: '/app/user/user.css'},
    { path: "/game", component: Game, html: '/app/game/game.html', css: '/app/game/game.css'},
    { path: "/waiting-room", component: WaitingRoom, html: '/app/waitingRoom/waiting.html', css: '/app/waitingRoom/waiting.css'},
    { path: "/credits", component: Credits, html: '/app/credits/credits.html', css: '/app/credits/credits.css'},
    { path: "/end-game", component: EndGame, html: '/app/endGame/endGame.html', css: '/app/endGame/endGame.css'},
    { path: "/404",component: PageNotFound, html: '/app/404/404.html', css: null}
];

export { routes, loadHTML };


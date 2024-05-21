import Home from './app/home/home.js';
import Login from './app/login/login.js';
import SignOut from './app/signout/signout.js';
import PageNotFound from './app/404/404.js';

const loadHTML = async (url) => {
    const response = await fetch(url);
    return await response.text();
};

const routes = [
    { path: "/", component: Home, html: '/app/home/home.html'},
    { path: "/login", component: Login, html: '/app/login/login.html', css: '/app/login/login.css'},
    { path: "/signout", component: SignOut, html: '/app/signout/signout.html' },
    { path: "/404",component: PageNotFound, html: '/app/404/404.html' }
];

export { routes, loadHTML };


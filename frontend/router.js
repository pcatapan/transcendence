import Home from './app/home/home.js';
import Login from './app/login/login.js';
import PageNotFound from './app/404/404.js';
import SignUp from './app/signUp/signUp.js';
import User from './app/user/user.js';

const loadHTML = async (url) => {
    const response = await fetch(url);
    return await response.text();
};

const routes = [
    { path: "/", component: Home, html: '/app/home/home.html', css : '/app/home/home.css'},
    { path: "/login", component: Login, html: '/app/login/login.html', css: '/app/login/login.css'},
    { path: "/sign-up", component: SignUp, html: '/app/signUp/signUp.html', css: '/app/signUp/signUp.css'},
    { path: "/user", component: User, html: '/app/user/user.html', css: '/app/user/user.css'},
    { path: "/404",component: PageNotFound, html: '/app/404/404.html', css: '/app/404/404.css'}
];

export { routes, loadHTML };


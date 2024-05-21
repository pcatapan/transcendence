import { routes, loadHTML } from '/router.js';

// Funzione per caricare CSS dinamicamente
const loadCSS = (url) => {
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onload = resolve;
        link.onerror = reject;
        document.head.appendChild(link);
    });
};

const navigateTo = url => {
    history.pushState(null, null, url);
    router();
};

document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", e => {
        if (e.target.matches("[data-link]")) {
            e.preventDefault();
            navigateTo(e.target.href);
        }
    });
    router();
});

const router = async () => {
    const potentialMatches = routes.map(route => {
        return {
            route: route,
            isMatch: location.pathname === route.path
        };
    });

    let match = potentialMatches.find(potentialMatch => potentialMatch.isMatch);

    if (!match) {
        match = {
            route: routes.find(route => route.path === "/404"),
            isMatch: true
        };
    }

    const view = await loadHTML(match.route.html);
    document.querySelector("#app").innerHTML = view;

    // Carica il CSS se definito
    if (match.route.css) {
        await loadCSS(match.route.css);
    }

    // Inizializza il componente
    if (match.route.component) {
        match.route.component();
    }
};

window.addEventListener("popstate", router);

import { showSnackbar } from '/utils/snackbar.js';
import { routes, loadHTML } from '/router.js';
import { authService } from '/services/auth.js';
import { APP_ENV } from '/enviroments.js';

const notAuthorizedRoutes = ["/login", "/sign-up"];

window.game = {
    mode : null,
    match_id : null,
    opponent : null,
    isActive : true
};

if (APP_ENV === 'development' && false) {
    window.game.mode = 'online';
    window.game.match_id = 27;
    window.game.opponent = {
        username: 'Opponent',
        avatar: 'https://www.gravatar.com/avatar/' + Math.floor(Math.random() * 1000000) + '?d=identicon'
    };
}

const checkAuthorization = async () => {
    try {
        const response = await authService.checkAuthorization();
        return response.status === 201;
    } catch (error) {
        return false;
    }
}

let loadedCSS = [];

// Funzione per caricare CSS dinamicamente
const loadCSS = (url) => {
    return new Promise((resolve, reject) => {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = url;
        link.onload = () => {
            loadedCSS.push(link);
            resolve();
        };
        link.onerror = reject;
        document.head.appendChild(link);
    });
};

// Funzione per rimuovere tutti i CSS caricati dinamicamente
const removeLoadedCSS = () => {
    loadedCSS.forEach(link => {
        document.head.removeChild(link);
    });
    loadedCSS = [];
};

const getURI = (url) => {
    let exploded = url.split("/").pop();
    return '/' + exploded;
}

window.navigateTo = async (url) => {
    if (!notAuthorizedRoutes.includes(getURI(url))) {
        let isAuthorized = await checkAuthorization();
        if (!isAuthorized) {
            url = "/login";
            showSnackbar("Devi essere loggato per poter accedere a questa pagina", "error");
        }
    }
    history.pushState(null, null, url);
    router();
};

/**
 * Interceptor per la gestione dei link
 * Se il link ha l'attributo data-link, allora viene intercettato
 * e gestito tramite il router
 */
document.addEventListener("DOMContentLoaded", () => {
    document.body.addEventListener("click", e => {
        if (e.target.matches("[data-link]")) {
            e.preventDefault();
            window.navigateTo(e.target.href);
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

    if (!notAuthorizedRoutes.includes(match.route.path)) {
        let isAuthorized = await checkAuthorization();
        if (!isAuthorized) {
            match = {
                route: routes.find(route => route.path === "/login"),
                isMatch: true
            };
            showSnackbar("Devi essere loggato per poter accedere a questa pagina", "error");
        }
    }


    const view = await loadHTML(match.route.html);
    document.querySelector("#app").innerHTML = view;

    // Rimuove tutti i CSS caricati dinamicamente
    removeLoadedCSS();

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
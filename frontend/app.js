import { showSnackbar } from '/utils/snackbar.js';
import { routes, loadHTML } from '/router.js';
import { authService } from '/services/auth.js';

const notAuthorizedRoutes = ["/login", "/sign-up"];


const checkAuthorization = async () => {
    try {
        const response = await authService.checkAuthorization();
        return response.status === 201;
    } catch (error) {
        return false;
    }
}

// window.ws = await initializeWebSocket();

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
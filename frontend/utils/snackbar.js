// snackbar.js
export function showSnackbar(message, type) {
    const snackbar = document.getElementById('snackbar');
    snackbar.className = 'snackbar show';
    snackbar.textContent = message;

    // Rimuove le classi esistenti dei tipi di snackbar
    snackbar.classList.remove('success', 'error', 'warning', 'info');

    // Aggiunge la classe del tipo di snackbar
    if (type) {
        snackbar.classList.add(type);
    }

    setTimeout(() => {
        snackbar.className = snackbar.className.replace('show', '');
    }, 3000);
}

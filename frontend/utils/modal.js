// modal.js

export function showModal(title, message, proprety) {
	const modal = document.getElementById('modal');
	const modalTitle = document.getElementById('modal-title');
	const modalMessage = document.getElementById('modal-content');

	modalTitle.textContent = title;
	modalMessage.textContent = message;

	modal.classList.add('modal-show');

	// rimuovo le proprietà già settate
	modal.style = '';

	if (proprety) {
		// stetto le proprietà come style
		for (let key in proprety) {
			modal.style[key] = proprety[key];
		}
	}
}

export function closeModal() {
	const modal = document.getElementById('modal');
	modal.classList.remove('modal-show');
}
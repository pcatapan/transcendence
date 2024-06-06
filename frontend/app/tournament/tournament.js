import { showSnackbar } from "../../utils/snackbar.js";
import { tournamentService } from "../../services/tournament-service.js";
import { gameMode } from "../../enviroments.js";

const Tournament = () => {

	document.querySelectorAll('.shape').forEach(shape => {
		shape.style.setProperty('--random-x', (Math.random() * 2 - 1).toFixed(2));
		shape.style.setProperty('--random-y', (Math.random() * 2 - 1).toFixed(2));
	}); 

	// Riferimenti agli elementi del DOM
	const modal = document.getElementById('tournamentModal');
	const closeModal = document.querySelector('.close');
	const addParticipantBtn = document.getElementById('addParticipantBtn');
	const participantNameInput = document.getElementById('participantName');
	const participantList = document.getElementById('participantList');
	const submitTournamentBtn = document.getElementById('submitTournamentBtn');
  
	let participants = [];
  
	if (!modal || !closeModal || !addParticipantBtn || !participantNameInput || !participantList || !submitTournamentBtn) {
	  return;
	}
  
	// Funzione per aprire la modale
	function openModal() {
	  modal.style.display = 'block';
	}
  
	// Funzione per chiudere la modale
	function closeModalFunc() {
	  modal.style.display = 'none';
	}
  
	// Aggiungi event listener per chiudere la modale
	closeModal.onclick = closeModalFunc;
	window.onclick = (event) => {
	  if (event.target === modal) {
		closeModalFunc();
	  }
	};
  
	// Funzione per aggiungere un partecipante
	addParticipantBtn.onclick = () => {
	  const participantName = participantNameInput.value.trim();
	  if (participantName) {
		participants.push(participantName);
		updateParticipantList();
		participantNameInput.value = '';
	  }
	};
  
	// Funzione per aggiornare la lista dei partecipanti
	function updateParticipantList() {
	  participantList.innerHTML = '';
	  participants.forEach((participant, index) => {
		const listItem = document.createElement('li');
		listItem.textContent = participant;
  
		const removeButton = document.createElement('button');
		removeButton.innerHTML = '&times;';
		removeButton.classList.add('btn');
		removeButton.onclick = () => {
		  removeParticipant(index);
		};
  
		listItem.appendChild(removeButton);
		participantList.appendChild(listItem);
	  });
	}
  
	// Funzione per rimuovere un partecipante
	function removeParticipant(index) {
	  participants.splice(index, 1);
	  updateParticipantList();
	}
  
	// Funzione per creare il torneo
	submitTournamentBtn.onclick = () => {
	  const tournamentTitle = document.getElementById('tournamentTitle').value.trim();
	  if (tournamentTitle && participants.length > 0) {

		// Chiamata al servizio per creare il torneo
		tournamentService.createTournament(tournamentTitle, participants).then((response) => {
		  if (response.status === 200) {
			showSnackbar('Tournament created successfully.', "success");
			document.getElementById('tournamentTitle').value = '';
			participants = [];
			updateParticipantList();
			closeModalFunc();

			const tournament = response.body['data']['tournament'];
    		const matches = response.body['data']['matches'];

			console.log('Tournament created successfully.');
			console.log(tournament);
			console.log(matches);

			// Salva i dati del torneo e delle partite nel localStorage
			localStorage.setItem('tournament', JSON.stringify(tournament));
			localStorage.setItem('matches', JSON.stringify(matches));

			window.game.mode = gameMode.tournament;

			window.navigateTo('/waiting-room');

		  } else {
			showSnackbar(`${response.body['message']}`, "error");
		  }
		});
	  } else {
		showSnackbar('Please enter the tournament title and at least one participant.', "error");
	  }
	};
  
	openModal();
  };
  
  document.addEventListener('DOMContentLoaded', Tournament);
  
  export default Tournament;
  
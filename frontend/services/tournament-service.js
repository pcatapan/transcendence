import { apiUrl } from '../enviroments.js';

const BASE_URL = apiUrl;

const headers = {
	'Content-Type': 'application/json',
	'Accept': '*/*'
};

export const tournamentService = {
	createTournament: async (name, participants) => {
		const response = await fetch(`${BASE_URL}/tournament/create`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({name : name, player_names : participants}),
		});
		return {status : response.status, body: await response.json()};
	},
	nextRound: async (tournamentId) => {
		const response = await fetch(`${BASE_URL}/tournament/next-round`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({tournament_id : tournamentId}),
		});
		return {status : response.status, body: await response.json()};
	},
};
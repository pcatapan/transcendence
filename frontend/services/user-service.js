import { apiUrl } from '../enviroments.js';

const BASE_URL = apiUrl;

const headers = {
	'Content-Type': 'application/json',
	'Accept': '*/*'
};

export const userService = {
	userProfile: async (id) => {
		const response = await fetch(`${BASE_URL}/user/show/${id}`, {
			method: 'GET',
			headers: headers,
		});
		return {status : response.status, body: await response.json()};
	},
};
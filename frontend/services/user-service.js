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
	removeFriend: async (id) => {
		const response = await fetch(`${BASE_URL}/user/friend/remove`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({user_id : id}),
		});
		return {status : response.status, body: await response.json()};
	},
	addFriend: async (id) => {
		const response = await fetch(`${BASE_URL}/user/friend/add`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({user_id : id}),
		});
		return {status : response.status, body: await response.json()};
	},
	disable2FA: async () => {
		const response = await fetch(`${BASE_URL}/disable_2fa`, {
			method: 'POST',
			headers: headers,
		});
		return {status : response.status, body: await response.json()};
	},
	enable2FA: async () => {
		const response = await fetch(`${BASE_URL}/enable_2fa`, {
			method: 'POST',
			headers: headers,
		});
		return {status : response.status, body: await response.json()};
	},

};
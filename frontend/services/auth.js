import { apiUrl } from '../enviroments.js';

const BASE_URL = apiUrl;

const headers = {
	'Content-Type': 'application/json',
	'Accept': '*/*'
};

export const authService = {
    loginIn: async (email, password) => {
		const response = await fetch(`${BASE_URL}/user/login`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({ email, password }),
		});
		return {status : response.status, body: await response.json()};
    },
	signUp: async (email, password, username, fullname) => {
		const response = await fetch(`${BASE_URL}/user/signup`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({ email, password, username, fullname }),
		});
		return {status : response.status, body: await response.json()};
	},
	checkAuthorization: async () => {
		const response = await fetch(`${BASE_URL}/authenticate`, {
			method: 'GET',
			headers: headers,
		});
		return {status : response.status};
	},
	logout: async () => {
		const response = await fetch(`${BASE_URL}/logout`, {
			method: 'GET',
			headers: headers,
		});
		return {status : response.status, body: await response.json()};
	},
	verifyOtp: async (user_id, totp_code) => {
		const response = await fetch(`${BASE_URL}/verify_totp_code`, {
			method: 'POST',
			headers: headers,
			body: JSON.stringify({ user_id, totp_code }),
		});
		return {status : response.status, body: await response.json()};
	},

};
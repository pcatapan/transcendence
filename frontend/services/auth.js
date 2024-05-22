import { apiUrlDev} from '../enviroments.js';

const BASE_URL = apiUrlDev;

export const authService = {
    loginIn: async (email, password) => {
		const response = await fetch(`${BASE_URL}/user/login`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': '*/*'
			},
			body: JSON.stringify({ email, password }),
		});
		return {status : response.status, body: await response.json()};
    },
	signUp: async (email, password, username, fullname) => {
		const response = await fetch(`${BASE_URL}/user/signup`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				'Accept': '*/*'
			},
			body: JSON.stringify({ email, password, username, fullname }),
		});
		return {status : response.status, body: await response.json()};
	}
};
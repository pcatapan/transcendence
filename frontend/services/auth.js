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
			body: JSON.stringify({ email, password })
		});

		const data = await response.json();
		return data;
    },
};
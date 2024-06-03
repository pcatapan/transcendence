import { showSnackbar } from '../../utils/snackbar.js';
import { authService } from '../../services/auth.js';

const SignUp = () => {

	const validatePassword = (password) => {
		const passwordPattern = /^(?=.*[A-Z])(?=.*[!@#$%^&*-])(?=.*[0-9]).{8,}$/;
		return passwordPattern.test(password);
	}

	const signUp = (event) => {
        event.preventDefault();

		const username = document.getElementById('username').value;
		const fullname = document.getElementById('fullname').value;
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

		if (!validatePassword(password)) {
			showSnackbar('Password must contain at least 8 characters, 1 uppercase letter, 1 special character and 1 number', 'error');
			return;
		}

        authService.signUp(email, password, username, fullname).then((response) => {
            if (response.status === 200) {
                showSnackbar(`${response.body['message']}`, 'success');
                setTimeout(() =>{
                    window.navigateTo('/');
                }, 500)
            }
            else{
                showSnackbar(`${response.body['message']}`, 'error');
            
            }
        })
        
    };

    document.getElementById('login-form').addEventListener('submit', signUp);
};
document.addEventListener('load', SignUp);

export default SignUp;
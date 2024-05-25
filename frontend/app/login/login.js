import { showSnackbar } from '../../utils/snackbar.js';
import { authService } from '../../services/auth.js';

const Login = () => {

    const logIn = (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        authService.loginIn(email, password).then((response) => {
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

    document.getElementById('login-form').addEventListener('submit', logIn);
};

document.addEventListener('load', Login);

export default Login;

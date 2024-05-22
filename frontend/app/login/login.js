import { showSnackbar } from '../../utils/snackbar.js';
import { authService } from '../../services/auth.js';

const Login = () => {
    // const validatePassword = (password) => {
    //     const passwordPattern = /^(?=.*[A-Z])(?=.*[!@#$%^&*])(?=.*[0-9]).{8,}$/;
    //     return passwordPattern.test(password);
    // };

    const logIn = (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        authService.loginIn(email, password).then((response) => {
            if (response.status === 200) {
                showSnackbar(`${response.body['message']}`, 'success');
                setTimeout(() =>{
                    window.location.href = '/';
                }, 500)
                localStorage.setItem('token', response.body['token']);
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

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

        console.log('Email:', email);
        console.log('Password:', password);

        authService.loginIn(email, password).then((response) => {
            console.log(response);
        })
        
    };

    document.getElementById('login-form').addEventListener('submit', logIn);
};

document.addEventListener('load', Login);

export default Login;

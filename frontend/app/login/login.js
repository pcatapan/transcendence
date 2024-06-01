import { showSnackbar } from '../../utils/snackbar.js';
import { authService } from '../../services/auth.js';
import { initializeWebSocket } from '../../websocket.js';

const Login = () => {

    const logIn = (event) => {
        event.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        authService.loginIn(email, password).then((response) => {
            if (response.status === 200) {
                showSnackbar(`${response.body['message']}`, 'success');

                initializeWebSocket();
                localStorage.setItem('user', response.body['data']['id']);
                
                setTimeout(() =>{
                    window.navigateTo('/');
                }, 500)
            }
            else if (response.status === 206) {
                // Open OTP modal
                document.getElementById('otp-modal').style.display = 'block';
                const user_id = response['body']['data'];

                document.getElementById('otp-submit').addEventListener('click', () => {
                    const otp = document.getElementById('otp').value;
                    authService.verifyOtp(user_id, otp).then((otpResponse) => {
                        if (otpResponse.status === 200) {
                            showSnackbar(`${otpResponse.body['message']}`, 'success');
                            localStorage.setItem('user', otpResponse.body['data']['id']);
                            setTimeout(() =>{
                                window.navigateTo('/');
                            }, 500);
                        } else {
                            showSnackbar(`${otpResponse.body['message']}`, 'error');
                        }
                    });
                });
            }
            else{
                showSnackbar(`${response.body['message']}`, 'error');
            
            }
        })
        
    };

    document.getElementById('close-otp-modal').onclick = function() {
            document.getElementById('otp-modal').style.display = "none";
        }

        // Close the modal if the user clicks anywhere outside of it
        window.onclick = function(event) {
            if (event.target == document.getElementById('otp-modal')) {
                document.getElementById('otp-modal').style.display = "none";
            }
        }

    document.getElementById('login-form').addEventListener('submit', logIn);
};

document.addEventListener('load', Login);

export default Login;

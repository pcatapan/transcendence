import { authService } from '../../services/auth.js';
import { showSnackbar } from '../../utils/snackbar.js';

const Home = () => {
    document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 2 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 2 - 1).toFixed(2));
    }); 
    
    document.getElementById('button-signout').addEventListener('click', function(event) {
        authService.logout().then((response) => {
            if (response.status === 200) {
                localStorage.clear();
                showSnackbar(`${response.body['message']}`, 'success');
                window.navigateTo('/login');
            }
            else{
                showSnackbar(`${response.body['message']}`, 'error');
            }
        })
    });
};

export default Home;
import { userService } from "../../services/user-service.js";
import { showSnackbar } from '../../utils/snackbar.js';
import { baseUrl } from '../../enviroments.js';

const User = () => {
    userService.userProfile(localStorage.getItem('user')).then((response) => {
        console.log(response);
        if (response.status === 200) {
            const user = response.body.data;
            
            const avatarElem = document.getElementById('avatar');
            if (avatarElem) avatarElem.src = baseUrl + user.avatar;

            const usernameElem = document.getElementById('username');
            if (usernameElem) usernameElem.innerHTML = '@' + user.username;

            const fullnameElem = document.getElementById('fullname');
            if (fullnameElem) fullnameElem.innerHTML = user.fullname;

            const emailElem = document.getElementById('email');
            if (emailElem) emailElem.innerHTML = user.email;

            const faElem = document.getElementById('2fa');
            if (faElem) faElem.innerHTML = (user['2FA'] === true) ? 'Attivo' : 'Disattivo';

            const eloElem = document.getElementById('elo');
            if (eloElem) eloElem.innerHTML = user.elo;

            const winsElem = document.getElementById('won-games');
            if (winsElem)  winsElem.innerHTML = user.user_stats.win_rate +' %';
            
            const lossesElem = document.getElementById('lost-games');
            if (lossesElem) lossesElem.innerHTML = user.user_stats.loss_rate+' %';

            const drawsElem = document.getElementById('draw-games');
            if (drawsElem) drawsElem.innerHTML = user.user_stats.tie_rate+' %';

            const tournamentGamesElem = document.getElementById('tournament-games');
            if (tournamentGamesElem) tournamentGamesElem.innerHTML = user.user_stats.tournaments_won;

            const lostGameNumerElem = document.getElementById('lost-games-number');
            if (lostGameNumerElem) lostGameNumerElem.innerHTML = user.user_stats.losses+'/'+user.user_stats.total_matches;

            const wonGameNumerElem = document.getElementById('won-games-number');
            if (wonGameNumerElem) wonGameNumerElem.innerHTML = user.user_stats.wins+'/'+user.user_stats.total_matches;

            const drawGameNumerElem = document.getElementById('draw-games-number');
            if (drawGameNumerElem) drawGameNumerElem.innerHTML = user.user_stats.tie +'/'+user.user_stats.total_matches;

            const friendsTableBody = document.querySelector('#friends-table tbody');
            if (friendsTableBody) {
                if (user.friends && user.friends.length > 0) {
                    user.friends.forEach(friend => {
                        const row = document.createElement('tr');
                        const avatarCell = document.createElement('td');
                        const usernameCell = document.createElement('td');

                        const avatar = document.createElement('img');
                        avatar.src = friend.avatar;
                        avatar.alt = 'Friend Avatar';
                        avatar.classList.add('friend-avatar');

                        const statusIndicator = document.createElement('span');
                        statusIndicator.classList.add('status-indicator');
                        statusIndicator.classList.add(friend.isOnline ? 'online' : 'offline');

                        avatarCell.appendChild(avatar);
                        avatarCell.appendChild(statusIndicator);
                        usernameCell.textContent = friend.username;

                        row.appendChild(avatarCell);
                        row.appendChild(usernameCell);

                        friendsTableBody.appendChild(row);
                    });
                } else {
                    const noFriendsRow = document.createElement('tr');
                    const noFriendsCell = document.createElement('td');
                    noFriendsCell.colSpan = 2;
                    noFriendsCell.textContent = 'No friends found';
                    noFriendsCell.style.textAlign = 'center';
                    noFriendsRow.appendChild(noFriendsCell);
                    friendsTableBody.appendChild(noFriendsRow);
                }
            }
        } else {
            showSnackbar(`${response.body.message}`, 'error');
        }
    });

    document.querySelectorAll('.shape').forEach(shape => {
        shape.style.setProperty('--random-x', (Math.random() * 2 - 1).toFixed(2));
        shape.style.setProperty('--random-y', (Math.random() * 2 - 1).toFixed(2));
    }); 
};

document.addEventListener('DOMContentLoaded', User);

export default User;

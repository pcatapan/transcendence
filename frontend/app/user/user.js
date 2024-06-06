import { userService } from "../../services/user-service.js";
import { showSnackbar } from '../../utils/snackbar.js';
import { baseUrl } from '../../enviroments.js';
import { authService } from "../../services/auth.js";

const User = () => {
    userService.userProfile(localStorage.getItem('user')).then((response) => {
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
            if (faElem) faElem.innerHTML = (user['2FA'] === true) ? 'Enabled' : 'Disabled';

            const btn2FA = document.getElementById('btn-2fa');
            if (btn2FA){
                if (user['2FA'] === true) {
                    btn2FA.style.backgroundColor = '#ff0000';
                    btn2FA.style.color = 'white';
                    btn2FA.style.border = 'none';
                    btn2FA.textContent = 'Disable 2FA';
                }
                else {
                    btn2FA.style.backgroundColor = '#00ff00';
                    btn2FA.style.color = 'black';
                    btn2FA.textContent = 'Enable 2FA';
                    btn2FA.style.border = 'none';
                }

                btn2FA.onclick = () => {
                    if (user['2FA'] === true){
                        userService.disable2FA().then((response) => {
                            if (response.status === 200) {
                                showSnackbar(`${response.body.message}`, 'success');
                                User();
                            } else {
                                showSnackbar(`${response.body.message}`, 'error');
                            }
                        });
                    }
                    else {
                        userService.enable2FA().then((response) => {
                            if (response.status === 206) {
                                showSnackbar(`${response.body.message}`, 'success');
                                // Show the modal with the QR code
                                const qrCodeModal = document.getElementById('qrCodeModal');
                                const qrCodeImage = document.getElementById('qrCodeImage');
                                const qrCodeMessage = document.getElementById('qrCodeMessage');
                                const closeModal = document.querySelector('.modal .close');
                                const continueButton = document.getElementById('continueButton');
                                const otpVerification = document.getElementById('otpVerification');

                                qrCodeImage.src = response.body.data;
                                qrCodeMessage.textContent = response.body.message;

                                qrCodeModal.style.display = 'block';

                                closeModal.onclick = () => {
                                    qrCodeModal.style.display = 'none';
                                };

                                window.onclick = (event) => {
                                    if (event.target === qrCodeModal) {
                                        qrCodeModal.style.display = 'none';
                                    }
                                };

                                continueButton.onclick = () => {
                                    // Hide the QR code and continue button
                                    qrCodeImage.style.display = 'none';
                                    continueButton.style.display = 'none';
                                    // Show the OTP input and verify button
                                    otpVerification.style.display = 'flex';
                                    qrCodeMessage.textContent = 'Enter the OTP code from the Authenticator app';
                                };

                                const verifyOtpButton = document.getElementById('verifyOtpButton');
                                verifyOtpButton.onclick = () => {
                                    const otpCode = document.getElementById('otpCode').value;
                                    authService.verifyOtp(user.id, otpCode).then((response) => {
                                        if (response.status === 200) {
                                            showSnackbar(`${response.body.message}`, 'success');
                                            qrCodeModal.style.display = 'none';
                                            User();  // Reload user data
                                        } else {
                                            showSnackbar(`${response.body.message}`, 'error');
                                        }
                                    })
                                };
                                // User();
                            } else {
                                showSnackbar(`${response.body.message}`, 'error');
                            }
                        });
                    
                    }
                }
            } 

            const editInfoBtn = document.getElementById('edit-info');
            const editUserInfoModal = document.getElementById('editUserInfoModal');
            const closeModal = document.querySelector('#editUserInfoModal .close');
            const editAvatarInput = document.getElementById('editAvatar');
            const editUsernameInput = document.getElementById('editUsername');
            const editFullnameInput = document.getElementById('editFullname');
            const editEmailInput = document.getElementById('editEmail');
            const saveUserInfoBtn = document.getElementById('saveUserInfoBtn');

            // Funzione per aprire la modale di modifica
            const openEditUserInfoModal = () => {
                // Carica i dati utente attuali nei campi di input
                editAvatarInput.value = ''; // Il campo file deve essere vuoto
                editUsernameInput.value = user.username;
                editFullnameInput.value = user.fullname;
                editEmailInput.value = user.email;

                editUserInfoModal.style.display = 'block';
            };

            // Funzione per chiudere la modale di modifica
            const closeEditUserInfoModal = () => {
                editUserInfoModal.style.display = 'none';
            };

            // Aggiungi event listener per aprire la modale di modifica
            if (editInfoBtn) {
                editInfoBtn.onclick = openEditUserInfoModal;
            }

            // Aggiungi event listener per chiudere la modale di modifica
            if (closeModal) {
                closeModal.onclick = closeEditUserInfoModal;
                window.onclick = (event) => {
                    if (event.target === editUserInfoModal) {
                        closeEditUserInfoModal();
                    }
                };
            
                // Funzione per salvare le modifiche
                saveUserInfoBtn.onclick = (event) => {
                    event.preventDefault();
            
                    const newUsername = editUsernameInput.value.trim();
                    const newFullname = editFullnameInput.value.trim();
                    const newEmail = editEmailInput.value.trim();
                    const newAvatarFile = editAvatarInput.files[0];

                    // Crea un oggetto FormData per inviare i dati del form, inclusi i file
                    if (newAvatarFile) {
                        const formData = new FormData();
                        formData.append('avatar', newAvatarFile);
                        userService.updateAvatar(formData).then((response) => {
                            if (response.status === 200) {
                                showSnackbar('Avatar updated successfully', 'success');
                                User();  // Reload the DOM to update avatar
                            } else {
                                showSnackbar(`${response.body.message}`, 'error');
                            }
                        })
                    }
          
                    // Effettua la chiamata API per aggiornare i dati dell'utente
                    userService.updateUserProfile(newUsername, newFullname, newEmail).then((response) => {
                        if (response.status === 200) {
                            showSnackbar('User profile updated successfully', 'success');
                            // Chiudi la modale dopo aver salvato le modifiche
                            closeEditUserInfoModal();
                            User()
                        } else {
                            showSnackbar(`${response.body.message}`, 'error');
                        }
                    })
                };
            };
            

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

            const friendsTable = document.getElementById("friends-table").getElementsByTagName('tbody')[0];
            friendsTable.innerHTML = ''; 
            const onlineUsers = JSON.parse(localStorage.getItem('onlineUsers')) || [];
            
            const noFriendsMessageElem = document.querySelector(".no-friends-message");
            if (noFriendsMessageElem) noFriendsMessageElem.remove();

            if (user.friends.length > 0) {
                user.friends.forEach(friend => {
                    const row = friendsTable.insertRow();

                    // Friend cell (Avatar + Username)
                    const friendCell = row.insertCell(0);
                    const avatarImg = document.createElement("img");
                    avatarImg.src = friend.avatar;
                    avatarImg.alt = friend.username;
                    avatarImg.classList.add("avatar");
                    friendCell.appendChild(avatarImg);

                    const usernameText = document.createElement("span");
                    usernameText.textContent = friend.username;
                    friendCell.appendChild(usernameText);

                    // Online/Offline status indicator
                    const statusIndicator = document.createElement("span");
                    const isOnline = onlineUsers.some(onlineUser => onlineUser.id === friend.id);
                    statusIndicator.classList.add('status-indicator');
                    statusIndicator.classList.add(isOnline ? 'online' : 'offline');
                    friendCell.appendChild(statusIndicator);

                    // Actions cell
                    const actionsCell = row.insertCell(1);
                    const actionDiv = document.createElement("div");
                    actionDiv.classList.add("action-buttons");

                    // Block/Unblock button
                    const removeButton = document.createElement("button");
                    removeButton.classList.add('btn');
                    removeButton.classList.add('button-table');

                    const removeIcon = document.createElement("img");
                    removeIcon.src = '../../assets/icons/trash.png';
                    removeIcon.alt = 'Remove';
                    removeIcon.classList.add('button-icon');

                    removeButton.appendChild(removeIcon);

                    removeButton.onclick = () => {
                        userService.removeFriend(friend.id).then((response) => {
                            if (response.status === 200) {
                                showSnackbar(`${response.body.message}`, 'success');
                                User();  // Reload the DOM to update friend list
                            } else {
                                showSnackbar(`${response.body.message}`, 'error');
                            }
                        });
                    };
                    actionDiv.appendChild(removeButton);

                    actionsCell.appendChild(actionDiv);
                });
            } else {
                const noFriendsMessage = document.createElement("p");
                noFriendsMessage.textContent = "There are no friends.";
                noFriendsMessage.classList.add("no-friends-message");
                document.getElementById("friends-table").appendChild(noFriendsMessage);
            }

            const matchHistoryTable = document.getElementById("match-history");
            const matchHistoryBody = matchHistoryTable.getElementsByTagName('tbody')[0];
            const matchHistoryHead = matchHistoryTable.getElementsByTagName('thead')[0];
            const matchHistoryContainer = document.getElementById("match-history-container");

            if (matchHistoryTable) {
                matchHistoryTable.innerHTML = '';  // Clear existing rows
            
                if (user.match_history && user.match_history.length > 0) {

                    if (matchHistoryHead) {
                        matchHistoryHead.classList.remove('hidden');
                    }
                    user.match_history.forEach(match => {
                        const row = matchHistoryTable.insertRow();
                        
                        // Date cell
                        const dateCell = row.insertCell(0);
                        const date = match.date_played ? new Date(match.date_played).toLocaleDateString() : '';
                        dateCell.textContent = date;
            
                        // Result cell
                        const resultCell = row.insertCell(1);
                        const result = document.createElement("span");
            
                        if (match.loser === null) {
                            result.innerText = 'Draw';
                            result.style.color = 'yellow';
                        } else if (match.loser === user.username) {
                            result.innerText = 'You Lose';
                            result.style.color = 'red';
                        } else {
                            result.innerText = 'You Won';
                            result.style.color = 'green';
                        }
            
                        resultCell.appendChild(result);
            
                        // Opponent cell
                        const opponentCell = row.insertCell(2);
                        const opponent = document.createElement("span");
            
                        if (match.loser === null) {
                            opponent.innerText = match.player1 === user.username ? match.player2 : match.player1;
                        } else if (match.loser === user.username) {
                            opponent.innerText = match.player1 === user.username ? match.player2 : match.player1;
                        } else {
                            opponent.innerText = match.player1 === user.username ? match.player2 : match.player1;
                        }
            
                        opponentCell.appendChild(opponent);
                    
                        // Score cell
                        const scoreCell = row.insertCell(3);
                        const score = `${match.player1_score} vs ${match.player2_score}`;
                        scoreCell.textContent = score;
                    
                        // Add friend button cell
                        const actionCell = row.insertCell(4);
                        const actionDiv = document.createElement("div");
                        actionDiv.classList.add("action-buttons");
            
                        const addButton = document.createElement("button");
                        addButton.classList.add('btn');
            
                        const addIcon = document.createElement("img");
                        addIcon.src = '../../assets/icons/addFriends.png';
                        addIcon.alt = 'ADD';
                        addIcon.classList.add('button-icon-add');
            
                        addButton.appendChild(addIcon);
            
                        const isFriend = user.friends.some(friend => friend.id === (user.id == match.player1_id ? match.player2_id : match.player1_id));
                        if (!isFriend) {
                            addButton.style.display = 'block';
                            addButton.onclick = () => {
                                userService.addFriend(user.id == match.player1_id ? match.player2_id : match.player1_id).then(response => {
                                    if (response.status === 200) {
                                        showSnackbar(`${response.body.message}`, 'success');
                                        User();  // Reload the DOM to update friend list
                                    } else {
                                        showSnackbar(`${response.body.message}`, 'error');
                                    }
                                });
                            };
                        } else {
                            addButton.style.display = 'none';
                        }
            
                        actionDiv.appendChild(addButton);
                        actionCell.appendChild(actionDiv);
                    });
                } else {
                    if (matchHistoryHead) {
                        matchHistoryHead.classList.add('hidden');
                    }
                    const noMatchesMessage = document.createElement("p");
                    noMatchesMessage.textContent = "No match history available.";
                    noMatchesMessage.classList.add("no-matches-message");
                    document.getElementById("match-history").appendChild(noMatchesMessage);
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

document.addEventListener('load', User);

export default User;

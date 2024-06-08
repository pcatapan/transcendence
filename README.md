<div align="center">

# Ft_trascendence


[![GitHub last commit](https://img.shields.io/github/last-commit/pcatapan/transcendence?color=blue&label=Last%20commit&logo=git&maxAge=3600)](https://github.com/pcatapan/transcendence/commits)

[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/pcatapan/transcendence?label=Code%20size&maxAge=3600)](https://github.com/pcatapan/transcendence)

</div>


## PONG vs PONG

<div align="center"">
  Welcome to our SPA website, where users engage in real-time matches against fellow players or challenge the intelligent AI for solo play. The project is dedicated to delivering a seamless and visually captivating user interface, enhancing the gaming experience for everyone. 
</div>

</br>
</br>

## Table of Contents

- [Features](#features)
- [Stack](#stack)
- [Game](#game)
- [Arquitecture](#arquitecture)

</br>
</br>

## Features

- **Real-time Multiplayer Pong:** Engage in exciting Pong matches with friends or other online players in a real-time multiplayer setup.

- **Play Against IA:** A working IA to  give you the oportunity to improve your gaming to impress your friends.

- **Authentication:** Standard User Authentication or 2FA implementation
  
- **Friends:** Users can add other users as friends and see their status (online, offline, in a game)

- **Match History:** Users can see his match history and the history
  
- **Tournaments:** Users can create tournaments

- **WAF:** Web Application Firewall to protect the website from attacks


</br>
</br>



## Stack

#### Front End
![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)

#### Back End
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)

#### DevOps
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Shell Script](https://img.shields.io/badge/shell_script-%23121011.svg?style=for-the-badge&logo=gnu-bash&logoColor=white)
Makefile


</br>
</br>


## Game

It is crucial for the game to have server-side functionality as the authoritative source of truth and control. This ensures a secure and fair gaming environment by preventing unauthorized manipulation or cheating on the client side. However, the acknowledgment of latency issues prompts the incorporation of front-end capabilities with JavaScript. This dual approach allows for a responsive and enjoyable user experience, where the front end can handle certain aspects of the game in real-time, minimizing the impact of latency on player interactions.

This balance between server-side robustness and front-end responsiveness contributes to an optimal and inclusive gaming experience for all users.

</br>
</br>



## Arquitecture

### Project Structure Overview

The project comprises various folders and files, each serving a distinct purpose.

The project structure segregates functionalities and components, dividing them into backend, frontend and configurations. Each directory contains specific updates and functionalities based on recent commits, aiming to enhance the overall user experience, server logic, and game functionalities.

- **Backend:** Handles the server-side logic and functionalities. Recent updates include enhancements related to lobby WebSocket and online status. Using as image base `python:3.7-alpine` and exposes de port 8000 to allow backend communication.
  
  The `settings.py` file determine the server's particular behavior, Dockerized environments, application management, database and the utilization of channels for real-time communication. Entails specific decisions regarding the server's implementation in a Dockerized environment and channel layers for asynchronous and real-time communication.

  The `urls.py` file manages URL routing by mapping specific URLs to corresponding views or endpoints within the Django server. It configures the API endpoints, WebSocket URLs, and serves static media files, controlling the handling of incoming requests in the web application.

  The `manage.py` script is Django's command-line tool used for administrative tasks. It configures the Django environment, executes management commands, and serves as the entry point for interacting with the Django project via the command line, facilitating tasks like database operations, server startup, and project management.

- **Frontend:** Single Page Applications (SPAs) operate by dynamically updating content on a single web page without requiring full page reloads. They utilize JavaScript to fetch data from the server, update the DOM, and manage user interactions seamlessly. Effective SPAs manage routing, allowing users to navigate within the app without causing full-page reloads, enhancing the user experience. Moreover, robust user authentication and identification play a pivotal role in SPAs, ensuring secure access to features, data, and resources. Proper authentication implementations enhance data security, privacy, and user trust by confirming the identity of individuals accessing the application, thereby safeguarding sensitive information and functionality.

- **Nginx:** Includes configurations and updates related to the NGINX web server, particularly in merging the develop branch.

  Within the Nginx configuration, settings for port 3000, typically used for Node.js applications or frontend services, might be established. Additionally, SSL/TLS configurations could be defined to ensure secure communication over HTTPS for enhanced data encryption and security measures. These SSL settings are crucial for encrypting data transmitted between clients and the server, particularly when dealing with sensitive information.

</br>
</br>
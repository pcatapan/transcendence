NAME = transcendence

$(NAME): run

run: create-js
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down
	rm -rf frontend/enviroments.js

create-js:
	@if [ ! -f .env ]; then \
		echo "Error: .env file not found. Would you like to create it from .env.example? Y/n" >&2; \
		read ans; \
		case "$$ans" in \
			[Yy]|[Yy][Ee][Ss]|"") \
				cp .env.example .env; \
				echo "Created .env from .env.example"; \
				;; \
			*) \
				echo "Aborting: .env file is required." >&2; \
				exit 1; \
				;; \
		esac \
	fi; \
	PORT=$$(awk -F'=' '/^NGINX_PORT=/{print $$2}' .env) ;\
	if [ -z "$$PORT" ]; then \
		echo "Error: NGINX_PORT not set in .env file." >&2; \
		exit 1; \
	fi; \
	HOSTNAME=$$(awk -F'=' '/^BACKEND_HOSTNAME=/{print $$2}' .env) ;\
	if [ -z "$$HOSTNAME" ]; then \
		echo "Error: BACKEND_HOSTNAME not set in .env file." >&2; \
		exit 1; \
	fi; \
	echo "export const apiUrl = 'http://$$HOSTNAME:$$PORT/api';" > frontend/enviroments.js ;\
	echo "export const webSocketUrl = 'ws://$$HOSTNAME:$$PORT/ws';" >> frontend/enviroments.js ;\
	echo "export const baseUrl = 'http://$$HOSTNAME:$$PORT';" >> frontend/enviroments.js ;\
	echo "" >> frontend/enviroments.js ;\
	echo "export const APP_ENV = 'development';" >> frontend/enviroments.js ;\
	echo "" >> frontend/enviroments.js ;\
	echo "// Modalità di gioco" >> frontend/enviroments.js ;\
	echo "export const gameMode = {" >> frontend/enviroments.js ;\
	echo "	online: 'online', // Due giocatori online" >> frontend/enviroments.js ;\
	echo "	offline: 'offline', // Due giocatori locali" >> frontend/enviroments.js ;\
	echo "	tournament: 'tournament', // Torneo" >> frontend/enviroments.js ;\
	echo "	ia_opponent: 'ia_opponent' // Avversario IA" >> frontend/enviroments.js ;\
	echo "};" >> frontend/enviroments.js

vclean:
	docker volume rm -f transcendence_postgres_data

iclean:
	docker image rm transcendence-daphne
	docker image rm transcendence-django
	docker image rm transcendence-nginx
	docker image rm postgres

clean: vclean iclean

fclean: down clean

re: fclean run
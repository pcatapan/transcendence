#!/bin/bash

PROJECT_DIR="/app/server/server"

./wait-for-it.sh transcendence_pg:5432

pip install --upgrade pip
pip install -r requirements.txt

# Check if the project directory already exists
if [ ! -d "$PROJECT_DIR" ]; then
    django-admin startproject server
else
    echo "Project directory '$PROJECT_DIR' already exists. Skipping project creation."
fi

cd server

# Run makemigrations and migrate
python3 manage.py makemigrations api
python3 manage.py makemigrations tournament
python3 manage.py makemigrations userauth
python3 manage.py makemigrations ws_api
python3 manage.py migrate

# Create superuser if it doesn't exist
python manage.py createsuperuser --username="$POSTGRES_USER" --email=admin@example.com --noinput

# Define a function for graceful shutdown
function graceful_shutdown() {
    echo "Received SIGTERM. Shutting down gracefully..."
    kill -TERM $PID
    wait $PID
    echo "Shutdown complete."
    exit 0
}

# Trap SIGTERM for graceful shutdown
trap graceful_shutdown SIGTERM

# Start the Django development server
python3 manage.py runserver 0.0.0.0:8000 &
PID=$!

# Wait for the process to finish
wait $PID
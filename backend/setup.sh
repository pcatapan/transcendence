#!/bin/bash

PROJECT_DIR="/app/server/server"

./wait-it.sh transcendence_pg:5432

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
python3 manage.py makemigrations authuser
python3 manage.py makemigrations ws
python3 manage.py migrate

# Create superuser if it doesn't exist
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='$POSTGRES_USER').exists())" | grep True; then python manage.py createsuperuser --username="$POSTGRES_USER" --email=admin@example.com --noinput
else
    echo "Superuser $POSTGRES_USER already exists. Skipping creation."
fi

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
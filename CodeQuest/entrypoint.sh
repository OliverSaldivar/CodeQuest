#!/bin/sh
set -e

echo "Esperando a que PostgreSQL este disponible en $POSTGRES_HOST:$POSTGRES_PORT..."
while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
  sleep 1
done
echo "PostgreSQL activo."

python manage.py makemigrations accounts curriculum challenges gamification analytics
python manage.py migrate
python manage.py seed_mvp

exec "$@"

python manage.py makemigrations chat
python manage.py migrate
gunicorn SynologyChatGPT.wsgi:application --bind 0.0.0.0:8000
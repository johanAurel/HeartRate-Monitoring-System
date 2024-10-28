sudo apt install sqlite3

pip install channels 

pip install paho-mqtt

pip install djangorestframework

pip install daphne

pip install channels_redis

pip install twisted[tls,http2]

python3 manage.py makemigrations

python3 manage.py migrate

python3 migrate.py collectstatic

# daphne -b 0.0.0.0 -p 8000 -u root heart_rate_monitor.asgi:application

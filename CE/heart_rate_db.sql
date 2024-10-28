-- Drop the database if it exists
DROP DATABASE IF EXISTS heart_rate_db;

-- Create a new database named heart_rate_db
CREATE DATABASE heart_rate_db;

-- Drop the user 'admin' if they exist
DROP USER IF EXISTS 'admin'@'%';

-- Create a new user 'admin' with the password '0000'
CREATE USER 'admin'@'%' IDENTIFIED BY '0000';

-- Grant all privileges on the heart_rate_db to the user 'admin'
GRANT ALL PRIVILEGES ON heart_rate_db.* TO 'admin'@'%';

-- Reload the privilege tables to ensure the changes take effect
FLUSH PRIVILEGES;

-- docker run -d -p 8000:8000 --name my_django_app -e "DB_USER=admin" -e "DB_PASSWORD=0000" my_django_image


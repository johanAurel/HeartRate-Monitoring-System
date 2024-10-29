### Directory Structure

Here’s the directory structure for the project:

```
heart_rate_monitor/
├── heart_rate_monitor/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   ├── routing.py
│   ├── auth_backend.py
│   ├── forms.py
│   ├── hidden.py
├── myapp/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── middleware.py
│   ├── consumer.py
│   ├── routing.py
│   ├── templates/
│                ├── base.html
│                ├── home.html
│                ├── user_list.html
│                ├── login.html
│                ├── register.html
│                ├── device_list.html
│                ├── logout.html
│                ├── heartbeat_rate.html
│                ├── add_device.html
│                ├── change_device_status.html
│   ├── static/
│                ├── css/
│                       ├──styles.css
│                ├── js/
│                       ├──websocker.js
├── manage.py
├── Dockerfile
├── command.sh
├── requirements.txt
```

### Step-by-Step Implementation

#### Step 1: Create a Django Project

1. **Install Django**:
   If you haven’t installed Django yet, you can do so using pip:
   ```bash
   pip install django
   ```

2. **Create a New Django Project**:
   ```bash
   django-admin startproject heart_rate_monitor
   cd heart_rate_monitor
   ```

3. **Create a New Django App**:
   ```bash
   python3 manage.py startapp myapp
   ```

#### Step 2: Update Settings

In `heart_rate_monitor/settings.py`, add your new app to `INSTALLED_APPS` and configure the database (using SQLite for simplicity):

#### Step 3: Define Models

In `myapp/models.py`, create a model for user devices and heart rate readings:

#### Step 4: Create Forms

In `myapp/forms.py`, create a form for user registration:


#### Step 5: Create Views

In `myapp/views.py`, create views for registration, login, monitoring heart rate, and handling abnormal readings:

#### Step 6: Implement Notifications

Create a simple notification function in `myapp/utils.py`:

#### Step 7: URL Routing

1. **Project URLs**: Update `heart_rate_monitor/urls.py` to include the app’s URLs.

2. **App URLs**: Created a `routing.py` file in the `heart_rate_monitor` directory:

#### Step 8: Created Templates

Created HTML templates in the `templates` folder:

1. **base.html**: Base template for extending other templates.( I created this one as the base page before you log in, then it becomes **home.html**)
2. The uses of the other templates are easier to understand in the `heart_rate_monitor/urls.py` path


#### Step 9: Apply Migrations

1. **Create Migrations**:
   ```bash
   python3 manage.py makemigrations
   ```

2. **Apply Migrations**:
   ```bash
   python3 manage.py migrate
   ```
3. **Collect updates made in your HTML, CSS or Websocket file**:
   ```bash
   python3 manage.py collectstatic
   ```

#### Step 10: Run the Development Server

Now that everything is set up, run the Django development server:

```bash
python3 manage.py runserver
```

Access the application by navigating to `localhost:8000/` in your web browser. You can register a new user, log in, and monitor heart rate readings.

### Summary

- **Django Project Setup**: We created a Django project and app for heart rate monitor.
- **Models**: Defined models to store user and heart rate data.
- **User Authentication**: Implemented user registration and login.
- **myapp**: Created a view to input heart rate readings and check for abnormal values.
- **Notifications**: Implemented a simple notification system to alert users of high heart rates.
- **Templates**: Developed HTML templates for user interaction.

#### Step 2: Create the `requirements.txt` File

Create a `requirements.txt` file to specify the required Python packages:

```plaintext
Django>=3.0,<4.0
requests
```

#### Step 11: Create the Dockerfile

Create a `Dockerfile` in the root of your project 

1. **Build the Docker Image**:
   ```bash
   docker build -t <your_dockerhub_username>/heart_rate_monitor:latest .
   ```

2. **Log in to Docker Hub**:
   ```bash
   docker login
   ```

3. **Push the Docker Image**:
   ```bash
   docker push <your_dockerhub_username>/heart_rate_monitor:latest
   ```
final steps(optional)

#### Step 12: Create Helm Chart

###Open Your Browser###
   Now, you can access the application at `http://localhost:8000/`.

### Summary

- **Django Project Setup**: Created a Django project for heart rate myapp.
- **Docker Containerization**: Created a Dockerfile to build and run the Django application in a container.
- **Helm Chart**: Created a Helm chart for deploying the application on Kubernetes.(optional)
- **Deployment**: Installed the Helm chart on the Kubernetes cluster.
- **Access the Application**: Used port forwarding to access the application locally.

This setup provides a robust framework for deploying your heart rate myapp application using Django and Helm on a Kubernetes cluster. If you have any questions or need further customization, feel free to ask!

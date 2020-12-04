# tradukejo

## How to install locally

Create a file `tradukejo/local_settings` with the following content:

```python
from tradukejo.settings import BASE_DIR

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '...'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

Here is an example of production configuration for MySQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tradukejo',
        'USER': 'user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

## Deploying

### After deploying for the first time:

Create the virtual environment in the project root folder with:

```console
$ python3 -m venv venv
```

Install the required packages:

```console
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Apply migrations, collect static files (see next section).

Create a superuser and load the list of languages to the database:

```console
$ python manage.py createsuperuser
$ python manage.py loaddata languages.json
```

### After each deployment

If there are new database migrations:

```console
$ source venv/bin/activate
$ python manage.py migrate
```

If there are changes in static files:

```console
$ python manage.py collectstatic
```

## Apache configuration

Here is an example of working Apache config:

```apache
<VirtualHost *:80>
	ServerName tradukejo.domain.com

	ServerAdmin webmaster@localhost
	DocumentRoot /var/www/tradukejo
	
	Alias /static /var/www/tradukejo/static

	<Directory /var/www/tradukejo/static>
		Require all granted
	</Directory>
	
	<Directory /var/www/tradukejo/tradukejo>
		<Files wsgi.py>
			Require all granted
		</Files>
	</Directory>
	
	WSGIDaemonProcess quiz python-home=/var/www/tradukejo/venv python-path=/var/www/tradukejo
	WSGIProcessGroup quiz
	WSGIScriptAlias / /var/www/tradukejo/tradukejo/wsgi.py

	ErrorLog ${APACHE_LOG_DIR}/tradukejo.error.log
	CustomLog ${APACHE_LOG_DIR}/tradukejo.access.log combined
</VirtualHost>
```

Do not forget to reload Apache after each deployment or change of Python file:

```console
# systemctl reload apache2
```

# tradukejo

## How to install locally

Rename the file `tradukejo/local_settings.py.template` to `local_settings.py` and set up your configuration there.

For production, don’t forget to update the email settings (see [Django documentation](https://docs.djangoproject.com/en/3.1/topics/email/), it’s also [possible to use `sendmail`](https://github.com/perenecabuto/django-sendmail-backend)).

In production, uncomment the last three lines for SCSS compilation (see [here](https://www.accordbox.com/blog/how-use-scss-sass-your-django-project-python-way/)):

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
$ python manage.py compress --force
```

## Vue.js

Vue.js is used for the translation interface (on only one page of the Django website). The Vue application is already compiled, but if you need to change it, go to `vue-translation-interface` and do:

```console
$ npm install
```

Instead of `npm run serve`, use:

```console
$ npm run build-watch
```

The application is recompiled on each change and the JS files are automatically exported to `traduko/static/traduko/vue-translation-interface`. Before deploying, do:

```console
$ npm run build
```

The whole `vue-translation-interface` folder is unnecessary in production.

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

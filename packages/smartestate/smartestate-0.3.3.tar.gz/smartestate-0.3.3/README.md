## SmartEstate

### About

Django app for real estate brokers. If you are a real estate broker, you can use this
to power your website, and the backend will allow you to manage your listings, apartments,
offers for sale, as well as potentials - renters, buyers, etc.

### Features

* Manage properties for rent and for sale
* Manage potential clients
* Manage your website, add custom pages
* Multilingual database: English, German, French, Spanish, Italian
* Your clients can filter available listings based on size, number of rooms, rent, etc.
* Vice versa: In SmartEstate's backend broker app, if your apartment has 3 rooms and monthly
  rent of $1000, you can click on it and SmartEstate shows you all registered clients who
  might be interested.

### Installing/usage

#### Pull latest Docker image

```
docker pull belalibrahim/smartestate:latest
```

#### Alternative: minimal docker-compose.yml

Paste the following into an empty file, name it _docker-compose.yml_,
run `docker compose up -d`, and then brose to http://localhost (or whatever host you specified).

```yaml
services:
  db:
    image: mysql:8.3
    restart: always
    environment:
      MYSQL_DATABASE: smartestate
      MYSQL_USER: smartestate
      MYSQL_PASSWORD: insecure-please-change
      MYSQL_ROOT_PASSWORD: insecure-please-change
    volumes:
      - db_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      timeout: 5s
      retries: 10

  web:
    image: belalibrahim/smartestate:latest
    restart: always
    ports:
      - "80:8000"
    environment:
      DEBUG: 0
      SECRET_KEY: insecure-please-change
      ALLOWED_HOSTS: localhost,127.0.0.1
      CSRF_TRUSTED_ORIGINS: "http://localhost,http://127.0.0.1"
      # Alternative: use these instead, if you have a public webserver
      #ALLOWED_HOSTS: your-web-host.com
      #CSRF_TRUSTED_ORIGINS: "https://*.your-web-host.com"
      DATABASE_ENGINE: django.db.backends.mysql
      DATABASE_HOST: db
      DATABASE_NAME: smartestate
      DATABASE_USER: smartestate
      DATABASE_PASSWORD: insecure-please-change
    depends_on:
      db:
        condition: service_healthy

volumes:
  db_data:
```

#### Alternative: Run locally from source via Docker Compose

```
git clone https://github.com/belal-i/smartestate
cd smartestate
docker compose up --detach --build
```

#### Advanced: Run locally from source via Django's runserver (for developers)

* Install platform requirements (for the MySQL driver, see https://github.com/PyMySQL/mysqlclient)

  - Debian/Ubuntu
    ```
    apt install  python3-dev default-libmysqlclient-dev  build-essential  pkg-config
    ```

  - Red Hat / CentOS
    ```
    yum install python3-devel mysql-devel pkgconfig
    ```

  - Other distros / macOS / Windows: See the [docs for mysqlclient](https://github.com/PyMySQL/mysqlclient), you probably have to
    install similar libraries. Otherwise, if you don't need MySQL (ie. using SQLite locally),
    you can comment out `mysqlclient` from the dependencies in _pyproject.toml_ and it should work.

* Build app from source code:
```
pip install .
```

* Alternative: Install Python package:
```
pip install --upgrade smartestate
```

* `cp .env.example .env` and configure with appropriate values.
* `python manage.py migrate`
* `python manage.py createsuperuser`
* `python manage.py runserver`
* Unit tests: `python manage.py test`

Set up the cookie group in the Django admin, and make it optional for the cookie banner to appear.

### Roadmap

This project is still in beta stage, there are still some issues, things might still be
a little unstable. However, it's come along nicely. If you decide to use this in production,
and encounter issues, please don't hesitate to open a ticket. Also, if you wish to contribute,
again, feel free to reach out :-)

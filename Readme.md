# Bounus Check Bot
___

## Запуск

Чтобы запустить проект, тебе понадобятся следующие инструменты
| Инструмент | Описание |
|----------|---------|
| [Python](https://www.python.org/downloads/) | Язык программирования |
| [Poetry](https://python-poetry.org/) | Менеджер зависимостей Python |

```Bash
# Клонируй через HTTPS:
$ git clone https://github.com/KerkaDev/BonusCheck_bot.git
# или через SSH:
$ git clone git@github.com:KerkaDev/BonusCheck_bot.git
$ cd BonusCheck_bot
```

1. Создать виртуальное окружение
```sh
[BonusCheck_bot] $ poetry config virtualenvs.in-project true
# Посмотри версию своего python
[BonusCheck_bot] $ python --version
[BonusCheck_bot] $ poetry env use версия_python
```
2. Активировать окружение
```sh
[BonusCheck_bot] $ source .venv/bin/activate
```
3. Установить библиотеки
```sh
(venv) [BonusCheck_bot] $ make install
```
4. Создайть базу данных

- Linux

```sh
$ sudo -u postgres psql
postgres=# CREATE DATABASE название_базы_данных;
postgres=# CREATE USER имя_пользователя WITH PASSWORD 'пароль'; 
postgres=# ALTER ROLE имя_пользователя SET client_encoding TO 'utf8';
postgres=# ALTER ROLE имя_пользователя SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE имя_пользователя SET timezone TO 'Europe/Moscow';
postgres=# GRANT ALL PRIVILEGES ON DATABASE название_базы_данных TO имя_пользователя;
postgres=# \q
```

- Windows

* В пуске находим и открываем SQL Shell
* Server [localhost]: Enter
* Database [postgres]: Enter
* Port [5432]: Enter
* Username [postgres]: Enter
* Пароль пользователя postgres: Введите пароль от postgres
```sh
postgres=# CREATE DATABASE название_базы_данных;
postgres=# CREATE USER имя_пользователя WITH PASSWORD 'пароль'; 
postgres=# ALTER ROLE имя_пользователя SET client_encoding TO 'utf8';
postgres=# ALTER ROLE имя_пользователя SET default_transaction_isolation TO 'read committed';
postgres=# ALTER ROLE имя_пользователя SET timezone TO 'Europe/Moscow';
postgres=# GRANT ALL PRIVILEGES ON DATABASE название_базы_данных TO имя_пользователя;
postgres=# \q
```

Добавить данные в файл `.env`

```sh
SQL_DATABASE="название_базы_данных"
SQL_USER="имя_пользователя"
SQL_PASSWORD="пароль"
SQL_HOST="localhost"
SQL_PORT=""
```
5. Сгенерировать в python пароль для django

```py
>> > from django.core.management.utils import get_random_secret_key
>> > get_random_secret_key()
'entwadfv&i6o'
```

Добавить данные в файл `.env`

```sh
SECRET_KEY="entwadfv&i6o"
```
Добавь остальные переменные в .env (Смотри .env.example)

6. Создать телеграм бота у bot father и получить api token

Добавить данные в файл `.env`

```sh
TELEGRAM_API_TOKEN="564jkA"
```

7. Запустить django

```sh
(venv) [BonusCheck_bot] $ make migrate
(venv) [BonusCheck_bot] $ make createsuperuser
(venv) [BonusCheck_bot] $ make run
```

8. Запустить бота

```sh
(venv) [BonusCheck_bot] $ make runbot
```

---

# Foodgram - продуктовый помощник
### Используется:

![example workflow](https://github.com/PythonGun/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)
[![Python](https://img.shields.io/badge/-Python_3.7.9-464646??style=flat-square&logo=Python)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/-Django-464646??style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django](https://img.shields.io/badge/-Django_rest_framework_3.12.4-464646??style=flat-square&logo=Django)](https://www.django-rest-framework.org)
![](https://img.shields.io/badge/Docker-3.8-yellow)
<br><br>

### Технологии
docker
gunicorn
ngnix
postgresql
yandex.cloud



## Описание
###### «Продуктовый помощник»: приложение, в котором пользователи публикуют рецепты, могут подписываться на публикации других авторов и добавлять рецепты в избранное. Сервис поможет пользователю создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

## Пользователи для проверки:
ivan@mail.ru 123e123e
petr@mail.ru  123e123e
## Проект доступен по адресу  http://158.160.2.214/recipes



# Развернуть проект локально
<details><summary>Локальная установка</summary>
 
_На Mac или Linux используем Bash_
_Для Windows PowerShell_

#### 1.Клонируем репозиторий на локальную машину:
```
https://github.com/PythonGun/foodgram-project-react
git clone https://github.com/PythonGun/foodgram-project-react.git
```
#### 2.Создать .env файл внутри директории infra (на одном уровне с docker-compose.yaml) Пример .env файла:
```
SECRET_KEY = 'ключ'
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

```
#### 3. Установка зависимостей:
#### Создаем и активируем виртуальное окружение:
Для Mac или Linux
```
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
```

Для Windows
```
python -m venv venv
source venv/Scripts/activate
cd backend
pip install -r requirements.txt
```
#### 4.Запуск Docker контейнеров: Запустите docker-compose
```
cd infra/
docker-compose up -d --build
```

#### 5.Выполните миграции, создайте суперпользователя и перенесите статику:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
```

#### 6.Проверьте доступность сервиса
```
http://localhost/admin
```

### Документация
```
http://localhost/redoc/
```
</details>


- :white_check_mark: [Баринов Денис](https://github.com/PythonGun)

# projectManager
Описание

Project Manager - это веб-приложение для управления проектами и задачами. Позволяет пользователям создавать проекты, назначать задачи, отслеживать прогресс и управлять комментариями.

Стек технологий

Backend: Django, Django REST Framework

Database: PostgreSQL

Docker: Используется для контейнеризации приложения

Установка и запуск

1. Клонирование репозитория

git clone https://github.com/mauk14/projectManager.git
cd projectManager

2. Создание .env файла

Создайте файл .env в корневой директории и добавьте:

DB_NAME=<название вашей базы>
DB_USER=<ваш пользователь>
DB_PASSWORD=<пароль>
DB_HOST=db
DB_PORT=5432

3. Запуск с Docker

Соберите и запустите контейнеры:

docker-compose up --build

После успешного запуска приложение будет доступно по адресу: http://localhost:8000/

4. Выполнение миграций (если не применились автоматически)

docker-compose exec web python project_manager/manage.py migrate

5. Создание суперпользователя (для входа в админ-панель)

docker-compose exec web python project_manager/manage.py createsuperuser

API

Документация API:

http://localhost:8000/api/docs/

Дополнительные команды

Остановка контейнеров:

docker-compose down

Очистка всех данных и контейнеров:

docker-compose down -v

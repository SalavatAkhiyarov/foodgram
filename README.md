# Foodgram
https://foodgram99.duckdns.org

## Описание
Foodgram — это веб-сервис для обмена рецептами.
Пользователи могут публиковать собственные рецепты, просматривать рецепты других участников, добавлять их в избранное и формировать список покупок.

### Ключевые возможности
- Публикация собственных рецептов с фотографиями и подробным описанием
- Просмотр и поиск рецептов других пользователей по тегам и ингредиентам
- Подписка на авторов, чтобы следить за их новыми рецептами
- Добавление рецептов в избранное для быстрого доступа
- Формирование и скачивание списка покупок по выбранным рецептам
- Регистрация и авторизация пользователей с личным кабинетом

## Технологический стек
В данном проекте используются следующие инструменты и библиотеки:
- **Python** — основной язык программирования для разработки
- **Django** — фреймворк для веб-разработки
- **Django REST Framework (DRF)** — библиотека для создания API
- **PostgreSQL** - база данных
- **pytest** - для тестирования
- **nginx** - веб-сервер и прокси
- **gunicorn** — WSGI-сервер для запуска Django-приложения
- **Docker** - контейнеризация и управление многоконтейнерным окружением
- **GitHub Actions** — CI/CD, автоматизация тестов и деплоя

## Как запустить проект
1. Клонировать репозиторий и перейти в него в командной строке:
git clone git@github.com:SalavatAkhiyarov/foodgram.git
cd foodgram_final
2. Убедитесь, что у вас установлен Docker и Docker Compose
3. Создайте файл .env в корне проекта и добавьте переменные:
SECRET_KEY=ваш_секретный_ключ
DB_NAME=название_бд
POSTGRES_USER=пользователь
POSTGRES_PASSWORD=пароль
DB_HOST=db
DB_PORT=5432
*Вы можете использовать пример .env.example*
4. Запустите процесс сборки контейнеров:
docker compose -f docker-compose.production.yml up --build
5. Примените миграции:
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
6. Соберите статические файлы:
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic

### Документация
Находясь в папке infra, выполните команду docker-compose up. При выполнении этой команды контейнер frontend, описанный в docker-compose.yml, подготовит файлы, необходимые для работы фронтенд-приложения, а затем прекратит свою работу.

По адресу http://localhost изучите фронтенд веб-приложения, а по адресу http://localhost/api/docs/ — спецификацию API.

## Автор
[Салават Ахияров](https://github.com/SalavatAkhiyarov)

[![Main Foodgram workflow](https://github.com/SalavatAkhiyarov/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/SalavatAkhiyarov/foodgram/actions/workflows/main.yml)

# Django REST Framework LMS Project

Проект системы управления обучением (LMS) на Django REST Framework с кастомной аутентификацией по email.

## 📋 Функциональность

### Модели данных
- **Пользователь** - кастомная модель с авторизацией по email
- **Курс** - образовательные курсы с превью и описанием
- **Урок** - уроки, связанные с курсами

### API Endpoints
- **CRUD операции** для курсов и уроков
- **RESTful API** с поддержкой всех HTTP методов
- **Вложенные сериализаторы** для отображения уроков в курсах

## 🛠 Технологии

- **Python 3.13**
- **Django 5.2.6**
- **Django REST Framework 3.16.1**
- **PostgreSQL** (с поддержкой SQLite для разработки)
- **Poetry** - управление зависимостями
- **Pillow** - работа с изображениями

## 📁 Структура проекта
```
Python_api_drf/
├── config/ # Настройки Django проекта
├── users/ # Приложение пользователей
│ ├── models.py # Кастомная модель User
│ ├── admin.py # Админка пользователей
│ └── ...
├── materials/ # Приложение материалов (курсы и уроки)
│ ├── models.py # Модели Course и Lesson
│ ├── serializers.py # Сериализаторы API
│ ├── views.py # ViewSet и Generic views
│ ├── urls.py # URL-маршруты API
│ └── ...
├── .env # Переменные окружения (не в git)
├── .gitignore # Git ignore файл
├── pyproject.toml # Зависимости Poetry
├── poetry.lock # Lock-файл Poetry
└── manage.py # Django management script
```
---

## ⚙️ Установка и запуск

### 1. Клонирование репозитория
```bash

git clone https://github.com/Umelyantsev-Vasily/Python_api_drf.git
cd Python_api_drf
```

## 2. Установка зависимостей

```
# Активация poetry окружения
poetry shell

# Или установка зависимостей
poetry install
```
## 3. Настройка окружения
Создайте файл .env в корне проекта:

```
SECRET_KEY=your-secret-key-here
DEBUG=True

# Для PostgreSQL
NAME=lms_db
USER=postgres
PASSWORD=your_password
HOST=localhost
PORT=5432

# Или используйте SQLite (раскомментируйте в settings.py)
```

## 4. Миграции базы данных
```
python manage.py makemigrations
python manage.py migrate
```

## 5. Создание суперпользователя
```
python manage.py createsuperuser
# Используйте email вместо username
```
## 6. Запуск сервера
```commandline
python manage.py runserver
```
## 🌐 API Endpoints
### Курсы (ViewSet)
- GET /api/courses/ - список всех курсов

- POST /api/courses/ - создание нового курса

- GET /api/courses/{id}/ - получение курса по ID

- PUT /api/courses/{id}/ - полное обновление курса

- PATCH /api/courses/{id}/ - частичное обновление курса

- DELETE /api/courses/{id}/ - удаление курса

### Уроки (Generic views)
- GET /api/lessons/ - список всех уроков

- POST /api/lessons/ - создание нового урока

- GET /api/lessons/{id}/ - получение урока по ID

- PUT /api/lessons/{id}/update/ - обновление урока

- DELETE /api/lessons/{id}/delete/ - удаление урока

# Education Platform

Django REST Framework project for online education platform.

## Функции
- Аутентификация и авторизация пользователей
- Управление курсами
- Интеграция платежей с Stripe
- Celery для фоновых задач
- Redis для кэширования
- База данных PostgreSQL

## Разработка
См. настройку docker-compose для локальной разработки.

## Лицензия:

Проект распространяется под [лицензией MIT](LICENSE)

## 👨‍💻 Разработчик
 ### Василий - tanec_991@mail.ru
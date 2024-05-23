
# Описание

<h2> Проект Blogicum.</h2>

# Установка (Windows):

Клонирование репозитория:

```sh
git clone https://github.com/Dmitriy-Bitsenko/django_sprint4
```
Переход в директорию django_sprint4
```sh
cd django_sprint4
```
Создание виртуального окружения
```sh
python -m venv venv
```
Активация виртуального окружения
```sh
source venv/Scripts/activate
```
Обновите pip
```sh
python -m pip install --upgrade pip
```
Установка зависимостей
```sh
pip install -r requirements.txt
```
Применение миграций
```sh
python manage.py migrate
```
Загрузить фикстуры в БД
```sh
python manage.py loaddata db.json
```
Создать суперпользователя
```sh
python manage.py createsuperuser
```
Запуск проекта
```sh
python manage.py runserver
```
Деактивация виртуального окружения
```sh
deactivate
```

# YaMDb API

## Описание

Проект YaMDb собирает отзывы пользователей на произведения. 

## Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/smirnovmn/api_yamdb
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env (для Linux/Mac)

python -m venv env (для Windows)
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip (для Linux/Mac)

python -m pip install --upgrade pip (для Windows)
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python3 manage.py migrate (для Linux/Mac)

python manage.py migrate (для Windows)
```

Запустить проект:

```
python3 manage.py runserver (для Linux/Mac)

python manage.py runserver (для Windows)
```

## Примеры

Получение списка всех произведений.
```
http://127.0.0.1:8000/api/v1/titles/
```

Получить список всех жанров.
```
http://127.0.0.1:8000/api/v1/genres/
```

Получение списка всех отзывов.
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```

Получение списка всех комментариев к отзыву.
```
http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

## Авторы проекта

- **Антон Авельев** — разработчик
- **Тимофей Глухов** — разработчик
- **Михаил Смирнов** — разработчик

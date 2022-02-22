# MyTube
MyTube - проект социальной сети в которой можно публиковать свои записи и комментировать чужие, подписываться на любимых авторов, ставить лайки и переписываться.
Проект находится в активной разработке.

## Технологии:

Django 3.2

JavaScript

Bootstrap 5

HTML

CSS

### Запуск проекта в dev-режиме
Клонировать репозиторий и перейти в него в командной строке. Создать и активировать виртуальное окружение c учетом версии Python 3.7:

```
git clone https://github.com/Seniacat/my_tube.git
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```
```
source env/bin/activate
```
Установить зависимости из файла requirements.txt:
```
python3 -m pip install --upgrade pip
```
```
pip install -r requirements.txt
```

Выполнить миграции:
```
python3 manage.py migrate
```
Запустить проект:
```
python3 manage.py runserver

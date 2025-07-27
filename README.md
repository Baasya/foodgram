## Foodgram 
#### проект доступен по адресу [https://foodgram.myftp.biz/](https://foodgram.myftp.biz/)
![иллюстрация проекта](https://github.com/Baasya/foodgram/blob/main/%D0%BF%D1%80%D0%B8%D0%BC%D0%B5%D1%80%20%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%BE%D0%B9%20%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D1%8B.png)
### Описание:
«Фудграм» — сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также будет доступен сервис «Список покупок». Он позволит создавать список продуктов, которые нужно купить для приготовления выбранных блюд. Документ со списком покупок доступен для скачивания.

###### Проект состоит из следующих страниц: 
* главная,
* страница входа,
* страница регистрации,
* страница рецепта,
* страница пользователя,
* страница подписок,
* избранное,
* список покупок,
* создание и редактирование рецепта,
* страница смены пароля,
  
## Для развёртывания проекта выполните следующие действия:

Клонируйте репозиторий на свой компьютер:
```
git clone https://github.com/Baasya/foodgram
```
Перейдите в директорию проекта:
```
cd foodgram
```
Создайте файл для хранения ключей доступа. Примеры значения переменных в файле .env.example :
```
touch .env
```
из директории infra запустите docker-compose.production:
```
sudo docker compose -f docker-compose.production.yml up
```
В терминале выполните миграции и сбор статики:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/
```
Создайте суперпользователя командой в терминале:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser
```
Импортируйте ингредиенты в базу данных:
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_csv ./data/ingredients.csv
```
#### Использованные технологии:
+ Python
+ Django
+ Django REST Framework
+ PostgreSQL
+ nginx
+ gunicorn
+ docker
+ GitHub Actions

##### Автор бэкенда и CI/CD реализации - Басюк Анастасия
###### 2025г

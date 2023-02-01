# Foodgram project

![example workflow](https://github.com/bour89/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)  

## Описание проекта 
 
Foodgram это сервис для публикации рецептов блюд. 

Ссылка на сайт: http://158.160.7.223
 
Ресурс позволяет публиковать собственные рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
 

## Запуск проекта

Для запуска проекта, нужно выполнить следующие шаги:

1. Установить Docker и Docker-compose. Пример установки на Ubuntu можно посмотреть [здесь](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-compose-on-ubuntu-20-04-ru).

Параметры описаны в конфигах `docker-compose.yml` и `nginx.conf` в директории `infra/`. При необходимости нужно добавить или изменить адреса проекта в файле `nginx.conf`

2. Запустить docker compose:
```
sudo docker-compose up -d --build
```
  
  После сборки создадутся три контейнера:
  > 1. контейнер базы данных `db`
  > 2. контейнер приложения `backend`
  > 3. контейнер web-сервера `nginx`
3. Создать миграции
```
sudo docker-compose exec backend python manage.py makemigrations
# в случае, если файлы миграций не формируются командой выше, запустить команду
# последовательно с указанием имен приложений users и recipes в следующем формате
sudo docker-compose exec backend python manage.py makemigrations [имя приложения]
```

4. Применить миграции:
```
sudo docker-compose exec backend python manage.py migrate
```

8. Создать супер-пользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```

9. Импортировать ингредиенты:
```
sudo docker-compose exec backend python manage.py import_ingredients
```

10. Собрать статику:
```
sudo docker-compose exec backend python manage.py collectstatic
```
# Install project

To install project on a local machine run these commands:
```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
(venv) $ flask --debug --app app run
...работает сервер, ctrl + c для выхода
(venv) $ deactivate
```

or simply run this script:
```
$ ./install.sh
```

# Run project
```
$ ./run.sh
```

and then  open your browser.

# TODO
1. Сделать хранилище для списка задач (для начала хранить в файле .json)
2. Сделать хранилище для списка задач на основании баз данных (самый простой вариант - БД SQLite)
2.1 SQLite
2.2 PostgreSQL - будем использовать "голые" запросы к БД при помощи pg8000 https://github.com/tlocke/pg8000/
2.3 POSTgreSQL - будем использовать вспомогат библ-ки (ORM) Alchemy https://www.sqlalchemy.org/ 
3. Доработать html (сделать правильную разметку), добавить стили css (будем использовать готовые стили)
4. Поддержка нескольких пользователей (форма регистрации (также кнопка log out), авторизация)
4.1 Форма авторизации
4.2 Регистрация нового пользователя
4.3 Опция log out
4.4 Разделение списка задач по пользователям (у каждого пользователя свой список задач)
4.5 Восстановление пароля путем отправки на личную почту
4.6 Реализовать отправку почты
4.7 Подтверждение почты
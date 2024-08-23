```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
(venv) $ flask --debug --app hello run
...работает сервер, ctrl + c для выхода
(venv) $ deactivate
```

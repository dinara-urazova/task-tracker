# Install project

To install project on local machine run these commands:
```bash
$ python3 -m venv .venv
$ . .venv/bin/activate
(venv) $ pip install --upgrade pip
(venv) $ pip install -r requirements.txt
(venv) $ flask --debug --app hello run
...работает сервер, ctrl + c для выхода
(venv) $ deactivate
```

or simple run this script:
```
$ ./install.sh
```

# Run project
```
$ ./run.sh
```

and then  open your browser.

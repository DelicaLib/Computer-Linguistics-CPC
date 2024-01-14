# Контрольная работа по "Компьютерной лингвистике"
---

## Server Ubuntu 18.04
Файлы в директории *server Ubuntu 18.04* необходимо запускать на Ubuntu 18.04.
Необходимые библиотеки:
```bash
pip install fastapi[all]
pip install transformers
pip install torch torchvision torchaudio
```
Также необходимо установить [томита-парсер](https://github.com/yandex/tomita-parser/). И установить символическую ссылку на него.

Чтобы запустить сервер необходимо прописать в консоли, находясь на одном уровне с *main.py* (Порт можно выбрать любой):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
``` 
## Database and Bot
Файлы в директории *Database and Bot* неможно запускать как на *Windows*, так и на *Linux*.
Используемая СУБД: PostgreSQL 16.
Необходимые библиотеки:
```bash
pip install telebot
pip install telegraph
pip install schedule
pip install python-dotenv
pip install requests
pip install bs4
pip install urllib3
pip install psycopg2
pip install urllib3
```
Также необходимо в этой директории создать файл .env, в котором указать (Заменить значения в кавычках на свои):
```bash
HOST="Хост, на котором находится база данных"
USER="Имя пользователя базы данных"
PASSWORD="Пароль от базы данных"
DB_NAME="Название базы данных"
PORT="Порт базы данных"

TOKEN="Токен бота в телеграм"
graph_token="Токен telegraph"
channel_id="Id канала в телеграм"
```

Чтобы запустить бота, необходимо запустить файл *bot.py* после того, как запуститься сервер на Ubuntu 18.04.
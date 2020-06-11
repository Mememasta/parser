# Parsing-avito

В этом руководстве мы настроим базу данных и виртуальное окружения. Установим из репозиториев Debian и из источников все необходимые пакеты и совместим их для работы под Linux Debian.

## Установка python3.5+ версии

[Ссылка на скачивание](https://www.python.org/ftp/python/3.7.7/Python-3.7.7.tar.xz)

Теперь установим загрузчик библиотек pip версии 3:

```
sudo apt-get install python3-pip
```

И установим дополнительные пакеты для работы некоторых библиотек python

```
sudo apt-get install python3 python-dev python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip libpg_dev
```

## Установка проекта

```
git clone https://github.com/Mememasta/parser
```

Все библиотеки уже лежат в файле env, поэтому достаточно активировать виртуальное окружение командой:

```
. env/bin/activate
```

Одна из возможных ошибок будет отсутствие пакета на Linux, установим его командой:

```
sudo apt-get install python3-virtualenv
```

Если виртуальное окружение не работает, установим библиотеки вручную

```
pip3 install -r requirements.txt
```

## Установка PostreSQL12

Установка postgresql достаточно сложная, ниже будет инструкция по полной настройке бд

```
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add - ; \
RELEASE=$(lsb_release -cs) ; \
echo "deb http://apt.postgresql.org/pub/repos/apt/ ${RELEASE}"-pgdg main | sudo tee  /etc/apt/sources.list.d/pgdg.list ; \
sudo apt update ; \
sudo apt -y install postgresql-12 ; \
sudo localedef ru_RU.UTF-8 -i ru_RU -fUTF-8 ; \
export LANGUAGE=ru_RU.UTF-8 ; \
export LANG=ru_RU.UTF-8 ; \
export LC_ALL=ru_RU.UTF-8 ; \
sudo locale-gen ru_RU.UTF-8 ; \
sudo dpkg-reconfigure locales
```

Добавьте локали в /etc/profile:

```
sudo vim /etc/profile #vim-редактор кода, можно использовать любой другой по типу nano
#после открытия редактора вписать след. строки
    export LANGUAGE=ru_RU.UTF-8
    export LANG=ru_RU.UTF-8
    export LC_ALL=ru_RU.UTF-8
```

Сменим пароль postgres, создадим пустую бд(особой надобности в ней нет, но сделать это нужно для будущих пунктов и назначения особых ролей пользователю):

```
sudo passwd postgres
su - postgres
export PATH=$PATH:/usr/lib/postgresql/12/bin

createdb --encoding UNICODE (любое название бд, без скобок) --username postgres
exit
```

Создание пользователя:

```
sudo -u postgres psql
postgres=# ...
create user (имя пользователя, не обязательно) with password 'пароль';
ALTER USER (имя пользователя) CREATEDB;
grant all privileges on database (название бд) to (имя пользователя);
\c (название бд)
GRANT ALL ON ALL TABLES IN SCHEMA public to (имя пользователя);
GRANT ALL ON ALL SEQUENCES IN SCHEMA public to (имя пользователя);
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public to (имя пользователя);
CREATE EXTENSION pg_trgm;
ALTER EXTENSION pg_trgm SET SCHEMA public;
UPDATE pg_opclass SET opcdefault = true WHERE opcname='gin_trgm_ops';
\q
exit
```
Теперь мы можем запустить файл "init_db.py" для создания всех таблиц, полей и пользователей

```
python3 app/init_db.py -a
```
Пояснение всех ключей

```
❯ python3 app/init_db.py --help
usage: init_db.py [-h] [-c] [-d] [-r] [-a]

optional arguments:
  -h, --help      Показать значение ключей и выйти
  -c, --create    Создать пустую бд и пользователя с разрешениями
  -d, --drop      Удалить бд и пользователя
  -r, --recreate  Удалить, после чего переустановить бд и пользователя
  -a, --all       Создать пример данных
```

В случае ошибки при запуске, возможным решением будет изменение конфигурации postgresql, а именно:

1) Заходим под пользователя postgres
```
sudo -u postgres psql
```
2) Смотрим путь до нужного нам файла
```
show hba_file ;

hba_file
--------------------------------------
/etc/postgresql/12/main/pg_hba.conf
```
3)Выходим из польз postgres и переходим по данному пути и меняем значения
!!! ВАЖНО: МЕНЯТЬ НУЖНО ЛИШЬ СТОЛБЕЦ METHOD т.е последний, все остально может отличаться
```
local   all             postgres                                peer

# TYPE  DATABASE        USER            ADDRESS                 METHOD

# "local" is for Unix domain socket connections only
local   all             all                                     trust
# IPv4 local connections:
host    all             all             127.0.0.1/32            trust
# IPv6 local connections:
host    all             all             ::1/128                 trust
# Allow replication connections from localhost, by a user with the
# replication privilege.
local   replication     all                                     trust
host    replication     all             127.0.0.1/32            trust
host    replication     all             ::1/128                 trust
```
4) Перезапустим postgresql

```
service postgresql restart
```

## Запуск приложения

1)Для вывода информации из бд используем следующую команду:

```
python3 app/main.py -c config/user_config.toml --view yes
```
-с это ключ для указания конфиг файла, в котором хранится хост, порт, имя бд, имя пользователя, пароль для подключения к бд
--view это ключ для вывода информации из бд

2) Для запуска парсинга и сохранения всех данных в бд используем команду:

```
python3 app/main.py -c config/user_config.toml --parsing yes
```
--parsing это ключ для активации парсинга сайта авито

## Возможные проблемы и ошибки проекта

После запуска проекта, ваш IP может быть забанен(НЕ БОЛЕЕ 30 МИНУТ БАНА) из-за превышения числа запросов в секунду, на практике выяснилось, что сайт позволяет совершать не больше 10 одновременных запросов в секунду в среднем

Были попытки исправить данный баг, но проблема состоит в том, что запросы посылаются ассинхронно, а парсинг каждого ответа разбит на потоки, из-за чего ставить ограничения(лимит) на количество запросов не вариант, принудительно замедлять sleep'ом не вариант, т.к функция синхронная, к большому сожалению подходящих вариантов как оставить высокую скорость работы и не превышать ограничение по req/sec найдено не было в связи нехватки времени

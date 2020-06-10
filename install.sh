#!/bin/bash
if psql -V
then
	echo "Запуск виртуального окружения"
	if . env/bin/activate
	then
		. env/bin/activate
		echo "Виртуальное окружение запущено"
	else
		echo "Окружение не было установлено"
		pip3 install -r requirements.txt

	fi

	echo "Создание базы данных"
	python3 app/init_db.py -a
else
	echo "---------------------------------"
	echo "ERROR: Установите PostreSql"
	echo "---------------------------------"
fi



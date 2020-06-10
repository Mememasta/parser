echo "1)Парсить авито и вывести данные"
echo "2)Вывести все данные из бд"

echo "Введите номер:"
read a

if $a=1
then
	python3 app/main.py -c config/user_config.toml --parsing yes
else
	python3 app/main.py -c config/user_config.toml --view yes
fi

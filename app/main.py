import argparse
import asyncio
import logging
import uvloop

from db import init_db, add_car, add_character, get_cars, get_characters
from settings import load_config, PACKAGE_NAME
from parsing import call_parsing_data

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

log = logging.getLogger(__name__)

async def add_cars(app):
    parse_list = await call_parsing_data()
    #add_cars = await Cars.add_cars(parse_data)
    #parse_list = [{'id': '5', 'Марка': 'ВАЗ (LADA)', 'Модель': '2113 Samara', 'Поколение': 'I (2004—2013)', 'Модификация': '1.6 MT (81 л.с.)', 'Год выпуска': '2007', 'Пробег': '204000', 'Состояние': 'не битый', 'Владельцев по ПТС': '3', 'VIN или номер кузова': 'XTA2*************', 'Тип кузова': 'хетчбэк', 'Количество дверей': '3', 'Тип двигателя': 'бензин', 'Коробка передач': 'механика', 'Привод': 'передний', 'Руль': 'левый', 'Цвет': 'чёрный', 'Комплектация': 'Базовая', 'Место осмотра': 'Республика Татарстан, Набережные Челны, 13-й комплекс, 9'}]
    if parse_list:
        async with app['db_pool'].acquire() as conn:
            for arr in parse_list:
                car = await add_car(conn, arr)
                character = await add_character(conn, arr)

    return parse_list

async def view_cars(app):
    async with app['db_pool'].acquire() as conn:
        car = await get_cars(conn)
        character = await get_characters(conn)
        return dict(car=car, character=character)


async def init_app(config):

    app = {}

    app['config'] = config

    db_pool = await init_db(app)

    log.debug(app['config'])
    
    if args.parsing:
        db = await add_cars(app)
        for key in db:
            print(key)
    
    if args.view:
        car_key = ['id', 'Марка', 'Модель', 'Поколение', 'Модификация', 'Год выпуска', 'Пробег', 'Состояние', 'Владельцев по ПТС', 'VIN или номер кузова', 'Цвет', 'Комплектация', 'Место осмотра', 'Дата парсинга']
        char_key = ['id', 'car_id', 'Тип кузова', 'Количество дверей', 'Тип двигателя', 'Коробка передач', 'Привод', 'Руль']
        db = await view_cars(app)
        for car in db['car']:
            i = 0
            print("---------------------------------------------------------------------------")
            for item in car:
                print(f'{car_key[i]}: {item}')
                i = i + 1
        for char in db['character']:
            i = 2
            for item in char[2:]:
                print(f'{char_key[i]}: {item}')
                i = i + 1
            print("---------------------------------------------------------------------------")

    return app

async def main(configpath):
    config = load_config(configpath)
    logging.basicConfig(level=logging.DEBUG)
    app = await init_app(config)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    parser.add_argument("--parsing", help="Спарсить данные с авито и вывести их")
    parser.add_argument("--view", help="Вывести все данные")
    args = parser.parse_args()
    event_loop = asyncio.get_event_loop()

    if args.config:
        event_loop.run_until_complete(main(args.config))
    else:
        parser.print_help()
